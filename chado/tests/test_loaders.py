"""Tests loaders functions."""

from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from chado.loaders.common import insert_organism, retrieve_organism
from chado.loaders.common import retrieve_ontology_term
from chado.loaders.ontology import OntologyLoader
from chado.loaders.sequence import SequenceLoader
from chado.models import CvtermDbxref, Cvtermsynonym, CvtermRelationship
from chado.models import Cv, Cvterm, Cvtermprop, Db, Dbxref, Organism, Feature
from django.test import TestCase
import obonet
import os


class SequenceTest(TestCase):
    """Tests Loaders - Common."""

    def test_store_sequence(self):
        """Tests - __init__."""
        Organism.objects.create(genus='Mus', species='musculus')
        test_db = Db.objects.create(name='SO')
        test_dbxref = Dbxref.objects.create(accession='00001', db=test_db)
        test_cv = Cv.objects.create(name='sequence')
        Cvterm.objects.create(name='assembly', cv=test_cv, dbxref=test_dbxref,
                              is_obsolete=0, is_relationshiptype=0)
        test_seq_file = SequenceLoader(file='sequence.fasta',
                                       organism='Mus musculus',
                                       soterm='assembly',
                                       url='http://teste.url',
                                       description='test sequence file')
        test_seq_obj = SeqRecord(Seq('acgtgtgtgcatgctagatcgatgcatgca'),
                                 id='chr1',
                                 description='chromosome 1')
        test_seq_file.store_sequence(test_seq_obj)
        test_feature = Feature.objects.get(uniquename='chr1')
        self.assertEqual('chromosome 1', test_feature.name)
        self.assertEqual('acgtgtgtgcatgctagatcgatgcatgca',
                         test_feature.residues)


class OntologyTest(TestCase):
    """Tests Loaders - Common."""

    def test_ontology(self):
        """Tests - __init__."""
        OntologyLoader('test_ontology', 'test_cv_definition')
        test_ontology = Cv.objects.get(name='test_ontology')
        self.assertEqual('test_ontology', test_ontology.name)
        self.assertEqual('test_cv_definition', test_ontology.definition)

        # Testing db_internal
        test_db_internal = Db.objects.get(name='internal')
        self.assertEqual('internal', test_db_internal.name)
        # Testing db_OBO_REL
        test_db_obo_rel = Db.objects.get(name='OBO_REL')
        self.assertEqual('OBO_REL', test_db_obo_rel.name)
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

        ontology = OntologyLoader('test_ontology', 'test_cv_definition')

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

        self.assertEqual(1, test_processed_cvterm_dbxref.is_for_definition)

    def test_process_cvterm_xref(self):
        """Tests - process_cvterm_xref."""
        ontology = OntologyLoader('test_ontology', 'test_cv_definition')

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

        ontology.process_cvterm_xref(test_cvterm, 'SP:xq')

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
        ontology = OntologyLoader('test_ontology', 'test_cv_definition')

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

    def test_process_cvterm_so_synonym(self):
        """Tests - process_cvterm_so_synonym."""
        ontology = OntologyLoader('test_ontology', 'test_cv_definition')

        test_db, created = Db.objects.get_or_create(name='test_go_synonym_db')
        test_dbxref, created = Dbxref.objects.get_or_create(
            db=test_db,
            accession='test_so_synonym_accession')

        test_cv, created = Cv.objects.get_or_create(
            name='test_so_synonym_cv')
        test_cvterm, created = Cvterm.objects.get_or_create(
            cv=test_cv,
            name='test_go_synonym_cvterm',
            dbxref=test_dbxref,
            is_relationshiptype=0,
            is_obsolete=0)

        ontology.process_cvterm_so_synonym(
                cvterm=test_cvterm,
                synonym='"stop codon gained" EXACT []')

        test_go_synonym = Cvtermsynonym.objects.get(
            cvterm=test_cvterm)
        test_go_type = Cvterm.objects.get(cvterm_id=test_go_synonym.type_id)

        self.assertEqual('stop codon gained', test_go_synonym.synonym)
        self.assertEqual('exact', test_go_type.name)

    def test_store_type_def(self):
        """Tests - store type_def."""
        directory = os.path.dirname(os.path.abspath(__file__))
        file = os.path.join(directory, 'data', 'so_trunc.obo')

        with open(file) as obo_file:
            G = obonet.read_obo(obo_file)

        cv_name = G.graph['default-namespace'][0]
        cv_definition = G.graph['data-version']
        # Initializing ontology
        ontology = OntologyLoader(cv_name, cv_definition)
        for typedef in G.graph['typedefs']:
            ontology.store_type_def(typedef)

        # Testing cv
        test_cv = Cv.objects.get(name='sequence')
        self.assertEqual('sequence', test_cv.name)
        self.assertEqual('so.obo(fake)', test_cv.definition)

        # Testing store_type_def
        test_db = Db.objects.get(name='_global')
        self.assertEqual('_global', test_db.name)
        test_dbxref = Dbxref.objects.get(db=test_db, accession='derives_from')
        self.assertEqual('derives_from', test_dbxref.accession)
        test_cvterm = Cvterm.objects.get(dbxref=test_dbxref)
        self.assertEqual('derives_from', test_cvterm.name)
        self.assertEqual('"testing def loading." [PMID:999090909]',
                         test_cvterm.definition)
        test_type = Cvterm.objects.get(name='comment')
        test_comment = Cvtermprop.objects.get(cvterm_id=test_cvterm.cvterm_id,
                                              type_id=test_type.cvterm_id)
        self.assertEqual('Fake typedef data.', test_comment.value)
        test_type = Cvterm.objects.get(name='is_class_level')
        test_prop = Cvtermprop.objects.get(cvterm_id=test_cvterm.cvterm_id,
                                           type_id=test_type.cvterm_id)
        self.assertEqual('1', test_prop.value)
        test_type = Cvterm.objects.get(name='is_metadata_tag')
        test_prop = Cvtermprop.objects.get(cvterm_id=test_cvterm.cvterm_id,
                                           type_id=test_type.cvterm_id)
        self.assertEqual('1', test_prop.value)
        test_type = Cvterm.objects.get(name='is_symmetric')
        test_prop = Cvtermprop.objects.get(cvterm_id=test_cvterm.cvterm_id,
                                           type_id=test_type.cvterm_id)
        self.assertEqual('1', test_prop.value)
        test_type = Cvterm.objects.get(name='is_transitive')
        test_prop = Cvtermprop.objects.get(cvterm_id=test_cvterm.cvterm_id,
                                           type_id=test_type.cvterm_id)
        self.assertEqual('1', test_prop.value)
        test_dbxref = Dbxref.objects.get(accession='0123')
        test_cvterm_dbxref = CvtermDbxref.objects.get(
            cvterm=test_cvterm, dbxref=test_dbxref)
        self.assertEqual(0, test_cvterm_dbxref.is_for_definition)

    def test_store_term(self):
        """Tests - store term."""
        directory = os.path.dirname(os.path.abspath(__file__))
        file = os.path.join(directory, 'data', 'so_trunc.obo')

        with open(file) as obo_file:
            G = obonet.read_obo(obo_file)

        cv_name = G.graph['default-namespace'][0]
        cv_definition = G.graph['data-version']
        # Initializing ontology
        ontology = OntologyLoader(cv_name, cv_definition)
        for typedef in G.graph['typedefs']:
            ontology.store_type_def(typedef)
        for n, data in G.nodes(data=True):
            ontology.store_term(n, data)

        # Testing store_term
        test_dbxref = Dbxref.objects.get(accession='0000013')
        test_cvterm = Cvterm.objects.get(dbxref=test_dbxref)
        self.assertEqual('scRNA', test_cvterm.name)
        test_def = Dbxref.objects.get(accession='ke')
        test_cvterm_dbxref = CvtermDbxref.objects.get(cvterm=test_cvterm,
                                                      dbxref=test_def)
        self.assertEqual(1, test_cvterm_dbxref.is_for_definition)
        test_alt_id_dbxref = Dbxref.objects.get(accession='0000012')
        test_alt_id = CvtermDbxref.objects.get(dbxref=test_alt_id_dbxref)
        test_alt_id_cvterm = Cvterm.objects.get(
            cvterm_id=test_alt_id.cvterm_id)
        self.assertEqual('scRNA', test_alt_id_cvterm.name)
        test_type = Cvterm.objects.get(name='comment')
        test_comment = Cvtermprop.objects.get(cvterm_id=test_cvterm.cvterm_id,
                                              type_id=test_type.cvterm_id)
        self.assertEqual('Fake term data.', test_comment.value)
        test_dbxref = Dbxref.objects.get(
            accession='http://web.site/FakeData "wiki"')
        test_cvterm_dbxref = CvtermDbxref.objects.get(
            cvterm=test_cvterm, dbxref=test_dbxref)
        self.assertEqual(0, test_cvterm_dbxref.is_for_definition)

    def test_store_relationship(self):
        """Tests - store relationship."""
        directory = os.path.dirname(os.path.abspath(__file__))
        file = os.path.join(directory, 'data', 'so_trunc.obo')

        with open(file) as obo_file:
            G = obonet.read_obo(obo_file)

        cv_name = G.graph['default-namespace'][0]
        cv_definition = G.graph['data-version']
        # Initializing ontology
        ontology = OntologyLoader(cv_name, cv_definition)
        for typedef in G.graph['typedefs']:
            ontology.store_type_def(typedef)
        for n, data in G.nodes(data=True):
            ontology.store_term(n, data)
        for u, v, type in G.edges(keys=True):
            ontology.store_relationship(u, v, type)

        # Testing store_term
        test_subject_dbxref = Dbxref.objects.get(accession='0000013')
        test_subject_cvterm = Cvterm.objects.get(dbxref=test_subject_dbxref)
        self.assertEqual('scRNA', test_subject_cvterm.name)
        test_object_dbxref = Dbxref.objects.get(accession='0000012')
        test_object_cvterm = Cvterm.objects.get(dbxref=test_object_dbxref)
        self.assertEqual('scRNA_primary_transcript', test_object_cvterm.name)

        test_type = CvtermRelationship.objects.get(
            subject=test_subject_cvterm, object=test_object_cvterm)
        test_type_cvterm = Cvterm.objects.get(cvterm_id=test_type.type_id)
        self.assertEqual('derives_from', test_type_cvterm.name)


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
