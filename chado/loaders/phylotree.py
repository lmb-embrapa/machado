"""Phylotree."""

from chado.loaders.exceptions import ImportingError
from chado.models import Cv, Cvterm, Db, Dbxref, Organism
from chado.models import Phylotree, Phylonode, PhylonodeOrganism
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
from typing import Optional


class PhylotreeLoader(object):
    """Load organism records."""

    def __init__(self, phylotree_name: str) -> None:
        """Execute the init function."""
        try:
            Phylotree.objects.get(name=phylotree_name)
            raise ImportingError(
                'Phylotree {} already exists'.format(phylotree_name))
        except ObjectDoesNotExist:
            pass

        try:
            self.db, created = Db.objects.get_or_create(
                name='DB:NCBI_taxonomy')
            dbxref, created = Dbxref.objects.get_or_create(
                db=self.db, accession='taxonomy')
            self.phylotree = Phylotree.objects.create(
                dbxref=dbxref, name=phylotree_name)

            self.level_db, created = Db.objects.get_or_create(
                name='species_taxonomy')
            self.level_cv, created = Cv.objects.get_or_create(
                name='taxonomy')
        except IntegrityError as e:
            raise ImportingError(e)

    def get_organism_by_accession(self, accession: int) -> Optional[Organism]:
        """Get organism by dbxref.accession."""
        try:
            organism_dbxref = Dbxref.objects.get(
                accession=accession, db=self.db)
            organism = Organism.objects.get(
                OrganismDbxref_organism_Organism__dbxref=organism_dbxref)
        except ObjectDoesNotExist:
            return None
        return organism

    def get_phylonode_by_accession(self, accession: int) -> Phylonode:
        """Get phylonode by dbxref.accession."""
        try:
            organism = self.get_organism_by_accession(accession)
            phylonode = Phylonode.objects.get(
                PhylonodeOrganism_phylonode_Phylonode__organism=organism)
        except ObjectDoesNotExist as e:
            raise ImportingError(e)
        return phylonode

    def store_phylonode_record(
            self, parent_id: Optional[int], tax_id: int,
            level: str, left_idx: int=0, right_idx: int=0):
        """Store phylonode record."""
        level_dbxref, created = Dbxref.objects.get_or_create(
            db=self.level_db, accession='taxonomy:{}'.format(level))
        level_cvterm, created = Cvterm.objects.get_or_create(
            cv=self.level_cv, dbxref=level_dbxref, name=level,
            defaults={'is_obsolete': 0, 'is_relationshiptype': 1})

        parent_phylonode_id = None
        if parent_id is not None:
            parent_phylonode = self.get_phylonode_by_accession(
                accession=parent_id)
            parent_phylonode_id = parent_phylonode.phylonode_id

        phylonode = Phylonode.objects.create(
            phylotree=self.phylotree,
            parent_phylonode_id=parent_phylonode_id,
            type_id=level_cvterm.cvterm_id,
            left_idx=left_idx, right_idx=right_idx)

        organism = self.get_organism_by_accession(accession=tax_id)
        PhylonodeOrganism.objects.create(
            phylonode=phylonode, organism=organism)
