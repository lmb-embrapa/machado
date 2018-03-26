"""Tests Loaders - Common."""

from machado.loaders.common import insert_organism, retrieve_organism
from machado.loaders.common import retrieve_ontology_term
from machado.models import Cv, Cvterm, Db, Dbxref, Organism
from django.test import TestCase


class CommonTest(TestCase):
    """Tests Loaders - Common."""

    def test_insert_organism_1(self):
        """Tests - insert_organism 1."""
        insert_organism(genus='Mus', species='musculus')
        test_organism_1 = Organism.objects.get(genus='Mus',
                                               species='musculus')
        self.assertEqual('Mus', test_organism_1.genus)
        self.assertEqual('musculus', test_organism_1.species)

    def test_insert_organism_2(self):
        """Tests - insert_organism 2."""
        test_db = Db.objects.create(name='test_db')
        test_dbxref = Dbxref.objects.create(accession='test_dbxref',
                                            db=test_db)

        test_cv = Cv.objects.create(name='test_cv')
        Cvterm.objects.create(name='test_cvterm',
                              cv=test_cv,
                              dbxref=test_dbxref,
                              is_obsolete=0,
                              is_relationshiptype=0)
        insert_organism(genus='Homo',
                        species='sapiens',
                        abbreviation='hs',
                        common_name='human',
                        comment='no comments',
                        type='test_cvterm')
        test_organism_2 = Organism.objects.get(genus='Homo',
                                               species='sapiens')
        self.assertEqual('Homo', test_organism_2.genus)
        self.assertEqual('sapiens', test_organism_2.species)
        self.assertEqual('hs', test_organism_2.abbreviation)
        self.assertEqual('human', test_organism_2.common_name)
        self.assertEqual('no comments', test_organism_2.comment)

    def test_retrieve_organism(self):
        """Tests - retrieve organism."""
        insert_organism(genus="Bos")
        insert_organism(genus="Bos", species="taurus")
        insert_organism(genus="Bos", species="taurus",
                        infraspecific_name="indicus")
        test_organism = retrieve_organism("Bos")
        self.assertEqual('Bos', test_organism.genus)
        test_organism = retrieve_organism("Bos taurus")
        self.assertEqual('taurus', test_organism.species)
        test_organism = retrieve_organism("Bos taurus indicus")
        self.assertEqual('indicus', test_organism.infraspecific_name)

    def test_retrieve_ontology_term(self):
        """Tests - retrieve ontology term."""
        test_db = Db.objects.create(name='sequence')
        test_dbxref = Dbxref.objects.create(db=test_db, accession='nucleotide')
        test_cv = Cv.objects.create(name='sequence')
        Cvterm.objects.create(
            cv=test_cv, dbxref=test_dbxref, name='nucleotide',
            is_obsolete=0, is_relationshiptype=0)
        test_ontology_cvterm = retrieve_ontology_term('sequence', 'nucleotide')
        test_ontology_cv = Cv.objects.get(cv_id=test_ontology_cvterm.cv_id)
        self.assertEqual('sequence', test_ontology_cv.name)
        self.assertEqual('nucleotide', test_ontology_cvterm.name)
