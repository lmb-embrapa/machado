# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Organism."""

from typing import List, Optional, Tuple

from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError

from machado.loaders.common import retrieve_organism
from machado.loaders.exceptions import ImportingError
from machado.models import Cv, Cvterm, Db, Dbxref
from machado.models import Organism, OrganismDbxref, Organismprop
from machado.models import OrganismPub, Pub


class OrganismLoader(object):
    """Load organism records."""

    def __init__(self, organism_db: str = None) -> None:
        """Execute the init function."""
        if organism_db is not None:
            self.db = Db.objects.create(name=organism_db)

        try:
            db_synonym, created = Db.objects.get_or_create(name="local")
            dbxref_synonym, created = Dbxref.objects.get_or_create(
                db=db_synonym, accession="synonym"
            )
            cv_synonym, created = Cv.objects.get_or_create(name="organism_property")
            self.cvterm_synonym, created = Cvterm.objects.get_or_create(
                cv=cv_synonym,
                name="synonym",
                is_obsolete=0,
                is_relationshiptype=1,
                dbxref_id=dbxref_synonym.dbxref_id,
            )
        except IntegrityError as e:
            raise ImportingError(e)

    # 'description='gi|1003052167|emb|CZF77396.1| 2-succinyl-6-hydroxy-2,
    # 4-cyclohexadiene-1-carboxylate synthase [Grimontia marina]'''
    def parse_scientific_name(self, scname: str) -> Tuple[str, str, Optional[str]]:
        """Parse scientific name."""
        fields = scname.split(" ")
        infra = None
        genus = fields[0]
        species = ".spp"
        # special case when there is no specific name...
        if len(fields) > 1:
            species = fields[1]
            if len(fields) > 2:
                infra = scname
        return (genus, species, infra)

    def store_organism_record(
        self, taxid: str, scname: str, synonyms: List[str], common_names: List[str]
    ) -> None:
        """Store organism record."""
        genus, species, infra = self.parse_scientific_name(scname)

        abbreviation = None
        if species is not None and species != ".spp":
            abbreviation = "{}. {}".format(genus[0], species)

        common_names_join = ",".join(common_names)

        organism = Organism.objects.create(
            genus=genus,
            species=species,
            infraspecific_name=infra,
            common_name=common_names_join,
            abbreviation=abbreviation,
        )

        if self.db:
            dbxref = Dbxref.objects.create(
                db=self.db, accession=taxid, description=scname
            )
            OrganismDbxref.objects.create(organism=organism, dbxref=dbxref)

        for i, synonym in enumerate(synonyms):
            Organismprop.objects.get_or_create(
                organism=organism,
                type_id=self.cvterm_synonym.cvterm_id,
                value=synonym,
                rank=i,
            )

    def store_organism_publication(self, organism: str, doi: str) -> None:
        """Store organism publication."""
        organism_obj = retrieve_organism(organism)

        try:
            doi_obj = Dbxref.objects.get(accession=doi, db__name="DOI")
            pub_obj = Pub.objects.get(PubDbxref_pub_Pub__dbxref=doi_obj)
        except ObjectDoesNotExist:
            raise ImportingError("{} not registered.", doi)

        OrganismPub.objects.get_or_create(organism=organism_obj, pub=pub_obj)
