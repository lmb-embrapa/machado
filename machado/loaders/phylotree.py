# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Phylotree."""

from typing import Dict, Optional, Tuple

from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError

from machado.loaders.exceptions import ImportingError
from machado.models import Cv, Cvterm, Db, Dbxref, Organism
from machado.models import Phylotree, Phylonode, PhylonodeOrganism


class PhylotreeLoader(object):
    """Load organism records."""

    def __init__(self, phylotree_name: str, organism_db: str) -> None:
        """Execute the init function."""
        try:
            Phylotree.objects.get(name=phylotree_name)
            raise ImportingError("Phylotree {} already exists".format(phylotree_name))
        except ObjectDoesNotExist:
            pass

        try:
            self.db, created = Db.objects.get_or_create(name=organism_db)
            dbxref, created = Dbxref.objects.get_or_create(
                db=self.db, accession="taxonomy"
            )
            self.phylotree = Phylotree.objects.create(
                dbxref=dbxref, name=phylotree_name
            )

            self.level_db, created = Db.objects.get_or_create(name="species_taxonomy")
            self.level_cv, created = Cv.objects.get_or_create(name="taxonomy")
            self.level_cvterms: Dict[str, Cvterm] = dict()
        except IntegrityError as e:
            raise ImportingError(e)

    def get_organism_by_accession(self, accession: int) -> Optional[Organism]:
        """Get organism by dbxref.accession."""
        try:
            organism_dbxref = Dbxref.objects.get(accession=accession, db=self.db)
            organism = Organism.objects.get(
                OrganismDbxref_organism_Organism__dbxref=organism_dbxref
            )
        except ObjectDoesNotExist:
            return None
        return organism

    def get_phylonode_by_accession(self, accession: int) -> Phylonode:
        """Get phylonode by dbxref.accession."""
        try:
            organism = self.get_organism_by_accession(accession)
            phylonode = Phylonode.objects.get(
                PhylonodeOrganism_phylonode_Phylonode__organism=organism
            )
        except ObjectDoesNotExist as e:
            raise ImportingError(e)
        return phylonode

    def update_parent_phylonode_id(self, phylonode_id: int, parent_id: int):
        """Update phylonode.parent_phylonode_id."""
        if parent_id is None:
            return
        parent_phylonode = self.get_phylonode_by_accession(accession=parent_id)
        phylonode = Phylonode.objects.get(phylonode_id=phylonode_id)
        phylonode.parent_phylonode_id = parent_phylonode.phylonode_id
        phylonode.save()

    def store_phylonode_record(
        self,
        parent_id: Optional[int],
        tax_id: int,
        level: str,
        left_idx: int = 0,
        right_idx: int = 0,
    ) -> Tuple[int, Phylonode]:
        """Store phylonode record."""
        level_cvterm = self.level_cvterms.get(level)
        if level_cvterm is None:
            level_dbxref, created = Dbxref.objects.get_or_create(
                db=self.level_db, accession=level
            )
            level_cvterm, created = Cvterm.objects.get_or_create(
                cv=self.level_cv,
                dbxref=level_dbxref,
                name=level,
                defaults={"is_obsolete": 0, "is_relationshiptype": 1},
            )
            self.level_cvterms[level] = level_cvterm

        parent_phylonode_id = None
        if parent_id is not None:
            parent_phylonode = self.get_phylonode_by_accession(accession=parent_id)
            parent_phylonode_id = parent_phylonode.phylonode_id

        phylonode = Phylonode.objects.create(
            phylotree=self.phylotree,
            parent_phylonode_id=parent_phylonode_id,
            type_id=level_cvterm.cvterm_id,
            left_idx=left_idx,
            right_idx=right_idx,
        )

        organism = self.get_organism_by_accession(accession=tax_id)
        if organism is None:
            raise ImportingError("Organism not found: {}".format(tax_id))
        organism.type_id = level_cvterm.cvterm_id
        organism.save()
        PhylonodeOrganism.objects.create(phylonode=phylonode, organism=organism)
        return (tax_id, phylonode)
