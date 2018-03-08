"""Taxonomy."""

from chado.loaders.exceptions import ImportingError
from chado.models import Db, Dbxref, Organism, OrganismDbxref
from django.db.utils import IntegrityError
from typing import Optional, Tuple


class OrganismLoader(object):
    """Load taxonomy: organism names and relationships."""

    def __init__(self, organism_db: str) -> None:
        """Execute the init function."""
        # Save DB taxonomy info
        try:
            self.db = Db.objects.create(name=organism_db)
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

    def store_ncbi_taxonomy_names_record(self,
                                         tax_id: str,
                                         scname: str) -> None:
        """Store Biopython SeqRecord."""
        dbxref = Dbxref.objects.create(
            db=self.db, accession=tax_id, description=scname)
        genus, species, infra = self.parse_scientific_name(scname)
        organism = Organism.objects.create(
            genus=genus, species=species, infraspecific_name=infra)
        OrganismDbxref.objects.create(organism=organism, dbxref=dbxref)
