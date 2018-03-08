"""Taxonomy."""

from chado.loaders.exceptions import ImportingError
from chado.models import Cv, Cvterm, Db, Dbxref
from chado.models import Organism, OrganismDbxref, Organismprop
from django.db.utils import IntegrityError
from typing import List, Optional, Tuple


class OrganismLoader(object):
    """Load taxonomy: organism names and relationships."""

    def __init__(self, organism_db: str) -> None:
        """Execute the init function."""
        # Save DB taxonomy info
        try:
            self.db = Db.objects.create(name=organism_db)

            db_synonym, created = Db.objects.get_or_create(
                name='local')
            dbxref_synonym, created = Dbxref.objects.get_or_create(
                db=db_synonym, accession='synonym')
            cv_synonym, created = Cv.objects.get_or_create(
                name='organism_property')
            self.cvterm_synonym, created = Cvterm.objects.get_or_create(
                cv=cv_synonym, name='synonym',
                is_obsolete=0, is_relationshiptype=1,
                dbxref_id=dbxref_synonym.dbxref_id)
        except IntegrityError as e:
            raise ImportingError(e)

    # 'description='gi|1003052167|emb|CZF77396.1| 2-succinyl-6-hydroxy-2,
    # 4-cyclohexadiene-1-carboxylate synthase [Grimontia marina]'''
    def parse_scientific_name(
            self, scname: str) -> Tuple[str, str, Optional[str]]:
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
            self, taxid: str, scname: str, synonyms: List[str],
            common_names: List[str]) -> None:
        """Store Biopython SeqRecord."""
        dbxref = Dbxref.objects.create(
            db=self.db, accession=taxid, description=scname)

        genus, species, infra = self.parse_scientific_name(scname)

        abbreviation = None
        if species is not None and species != '.spp':
            abbreviation = '{}. {}'.format(genus[0], species)

        common_names_join = ','.join(common_names)

        organism = Organism.objects.create(
            genus=genus, species=species, infraspecific_name=infra,
            common_name=common_names_join, abbreviation=abbreviation)

        OrganismDbxref.objects.create(organism=organism, dbxref=dbxref)

        for i, synonym in enumerate(synonyms):
            Organismprop.objects.get_or_create(
                organism=organism, type_id=self.cvterm_synonym.cvterm_id,
                value=synonym, rank=i)
