"""Tests loaders functions."""

from chado.loaders.common import insert_organism
from chado.loaders.ontology import Ontology
from chado.models import CvtermDbxref, Cvtermsynonym
from chado.models import Cv, Cvterm, Db, Dbxref, Organism
from django.test import TestCase


class OntologyTest(TestCase):
    """Tests Loaders - Common."""

    def test_ontology(self):
        """Tests - preprocessing."""
        Ontology('test_ontology',
                 'test_cv_definition')
        test_ontology = Cv.objects.get(name='test_ontology')
        self.assertEqual('test_ontology', test_ontology.name)
        self.assertEqual('test_cv_definition', test_ontology.definition)

        # Testing db_internal
        test_db_internal = Db.objects.get(name='internal')
        self.assertEqual('internal', test_db_internal.name)
        # Testing db_obo_rel
        test_db_obo_rel = Db.objects.get(name='obo_rel')
        self.assertEqual('obo_rel', test_db_obo_rel.name)
        # Testing db__global
        test_db__global = Db.objects.get(name='_global')
        self.assertEqual('_global', test_db__global.name)

        # Testing cv_synonym_type
        test_cv_synonym_type = Cv.objects.get(name='synonym_type')
        self.assertEqual('synonym_type', test_cv_synonym_type.name)
        # Testing cv_relationship
        test_cv_relationship = Cv.objects.get(name='relationship')
        self.assertEqual('relationship', test_cv_relationship.name)
        # Testing cv_cvterm_property_type
        test_cv_cvterm_property_type = Cv.objects.get(
            name='cvterm_property_type')
        self.assertEqual('cvterm_property_type',
                         test_cv_cvterm_property_type.name)

        # Testing cvterm is_symmetric
        test_dbxref_is_symmetric = Dbxref.objects.get(accession='is_symmetric',
                                                      db=test_db_internal)
        test_cvterm_is_symmetric = Cvterm.objects.get(
            name='is_symmetric', cv=test_cv_cvterm_property_type)
        self.assertEqual('is_symmetric', test_dbxref_is_symmetric.accession)
        self.assertEqual('is_symmetric', test_cvterm_is_symmetric.name)

        # Testing cvterm is_anti_symmetric
        test_dbxref_is_anti_symmetric = Dbxref.objects.get(
            accession='is_anti_symmetric', db=test_db_internal)
        test_cvterm_is_anti_symmetric = Cvterm.objects.get(
            name='is_anti_symmetric', cv=test_cv_cvterm_property_type)
        self.assertEqual('is_anti_symmetric',
                         test_dbxref_is_anti_symmetric.accession)
        self.assertEqual('is_anti_symmetric',
                         test_cvterm_is_anti_symmetric.name)

        # Testing cvterm comment
        test_dbxref_comment = Dbxref.objects.get(accession='comment',
                                                 db=test_db_internal)
        test_cvterm_comment = Cvterm.objects.get(
            name='comment', cv=test_cv_cvterm_property_type)
        self.assertEqual('comment', test_dbxref_comment.accession)
        self.assertEqual('comment', test_cvterm_comment.name)

        # Testing cvterm is_a
        test_dbxref_is_a = Dbxref.objects.get(accession='is_a',
                                              db=test_db_obo_rel)
        test_cvterm_is_a = Cvterm.objects.get(
            name='is_a', cv=test_cv_relationship)
        self.assertEqual('is_a', test_dbxref_is_a.accession)
        self.assertEqual('is_a', test_cvterm_is_a.name)

        # Testing cvterm is_transitive
        test_dbxref_is_transitive = Dbxref.objects.get(
            accession='is_transitive', db=test_db_internal)
        test_cvterm_is_transitive = Cvterm.objects.get(
            name='is_transitive', cv=test_cv_cvterm_property_type)
        self.assertEqual('is_transitive',
                         test_dbxref_is_transitive.accession)
        self.assertEqual('is_transitive',
                         test_cvterm_is_transitive.name)

        # Testing cvterm is_reflexive
        test_dbxref_is_reflexive = Dbxref.objects.get(
            accession='is_reflexive', db=test_db_internal)
        test_cvterm_is_reflexive = Cvterm.objects.get(
            name='is_reflexive', cv=test_cv_cvterm_property_type)
        self.assertEqual('is_reflexive',
                         test_dbxref_is_reflexive.accession)
        self.assertEqual('is_reflexive',
                         test_cvterm_is_reflexive.name)

        # Testing cvterm is_class_level
        test_dbxref_is_class_level = Dbxref.objects.get(
            accession='is_class_level', db=test_db_internal)
        test_cvterm_is_class_level = Cvterm.objects.get(
            name='is_class_level', cv=test_cv_cvterm_property_type)
        self.assertEqual('is_class_level',
                         test_dbxref_is_class_level.accession)
        self.assertEqual('is_class_level',
                         test_cvterm_is_class_level.name)

        # Testing cvterm is_metadata_tag
        test_dbxref_is_metadata_tag = Dbxref.objects.get(
            accession='is_metadata_tag', db=test_db_internal)
        test_cvterm_is_metadata_tag = Cvterm.objects.get(
            name='is_metadata_tag', cv=test_cv_cvterm_property_type)
        self.assertEqual('is_metadata_tag',
                         test_dbxref_is_metadata_tag.accession)
        self.assertEqual('is_metadata_tag',
                         test_cvterm_is_metadata_tag.name)

    def test_process_cvterm_def(self):
        """Tests - process_cvterm_def."""
        definition = '"A gene encoding ..." [SO:xp]'

        ontology = Ontology('test_ontology', 'test_cv_definition')

        test_db, created = Db.objects.get_or_create(name='test_def_db')
        test_dbxref, created = Dbxref.objects.get_or_create(
            db=test_db, accession='test_def_accession')

        test_cv, created = Cv.objects.get_or_create(
            name='test_def_cv')
        test_cvterm, created = Cvterm.objects.get_or_create(
            cv=test_cv,
            name='test_def_cvterm',
            dbxref=test_dbxref,
            is_relationshiptype=0,
            is_obsolete=0)

        ontology.process_cvterm_def(test_cvterm, definition)

        test_processed_db = Db.objects.get(name='SO')
        test_processed_dbxref = Dbxref.objects.get(db=test_processed_db,
                                                   accession='xp')

        test_processed_cvterm_dbxref = CvtermDbxref.objects.get(
            cvterm=test_cvterm,
            dbxref=test_processed_dbxref)

        self.assertEqual(0, test_processed_cvterm_dbxref.is_for_definition)

    def test_process_cvterm_xref(self):
        """Tests - process_cvterm_xref."""
        ontology = Ontology('test_ontology', 'test_cv_definition')

        test_db, created = Db.objects.get_or_create(name='test_xref_db')
        test_dbxref, created = Dbxref.objects.get_or_create(
            db=test_db,
            accession='test_xref_accession')

        test_cv, created = Cv.objects.get_or_create(name='test_xref_cv')
        test_cvterm, created = Cvterm.objects.get_or_create(
            cv=test_cv,
            name='test_xref_cvterm',
            dbxref=test_dbxref,
            is_relationshiptype=0,
            is_obsolete=0)

        ontology.process_cvterm_xref(test_cvterm, 'SP:xq', 0)

        test_processed_db = Db.objects.get(name='SP')
        test_processed_dbxref = Dbxref.objects.get(
            db=test_processed_db,
            accession='xq')

        test_processed_cvterm_dbxref = CvtermDbxref.objects.get(
            cvterm=test_cvterm,
            dbxref=test_processed_dbxref)

        self.assertEqual(0, test_processed_cvterm_dbxref.is_for_definition)

    def test_process_cvterm_go_synonym(self):
        """Tests - process_cvterm_go_synonym."""
        ontology = Ontology('test_ontology', 'test_cv_definition')

        test_db, created = Db.objects.get_or_create(name='test_go_synonym_db')
        test_dbxref, created = Dbxref.objects.get_or_create(
            db=test_db,
            accession='test_go_synonym_accession')

        test_cv, created = Cv.objects.get_or_create(
            name='test_go_synonym_cv')
        test_cvterm, created = Cvterm.objects.get_or_create(
            cv=test_cv,
            name='test_go_synonym_cvterm',
            dbxref=test_dbxref,
            is_relationshiptype=0,
            is_obsolete=0)

        ontology.process_cvterm_go_synonym(
                cvterm=test_cvterm,
                synonym='"30S ribosomal subunit" [GOC:mah]',
                synonym_type='related_synonym')

        test_go_synonym = Cvtermsynonym.objects.get(
            cvterm=test_cvterm,
            synonym='30S ribosomal subunit')

        self.assertEqual('30S ribosomal subunit', test_go_synonym.synonym)


class CommonTest(TestCase):
    """Tests Loaders - Common."""

    def test_insert_organism_1(self):
        """Tests - insert_organism 1."""
        insert_organism('Mus', 'musculus')
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
        test_cvterm = Cvterm.objects.create(name='test_cvterm',
                                            cv=test_cv,
                                            dbxref=test_dbxref,
                                            is_obsolete=0,
                                            is_relationshiptype=0)
        insert_organism(genus='Homo',
                        species='sapiens',
                        abbreviation='hs',
                        common_name='human',
                        comment='no comments',
                        type_id=test_cvterm.cvterm_id)
        test_organism_2 = Organism.objects.get(genus='Homo',
                                               species='sapiens')
        self.assertEqual('Homo', test_organism_2.genus)
        self.assertEqual('sapiens', test_organism_2.species)
        self.assertEqual('hs', test_organism_2.abbreviation)
        self.assertEqual('human', test_organism_2.common_name)
        self.assertEqual('no comments', test_organism_2.comment)
