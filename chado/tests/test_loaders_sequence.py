"""Tests loader sequence."""

from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from chado.loaders.sequence import SequenceLoader
from chado.loaders.publication import PublicationLoader
from chado.models import Feature, FeaturePub
from chado.models import Pub, PubDbxref
from chado.models import Cv, Cvterm, Db, Dbxref, Organism
from django.test import TestCase
from bibtexparser.bibdatabase import BibDatabase


class SequenceTest(TestCase):
    """Tests Loaders - SequenceLoader."""

    def test_store_biopython_seq_record(self):
        """Tests - __init__ and store_biopython_seq_record."""
        Organism.objects.create(genus='Mus', species='musculus')
        test_db = Db.objects.create(name='SO')
        test_dbxref = Dbxref.objects.create(accession='00001', db=test_db)
        test_cv = Cv.objects.create(name='sequence')
        Cvterm.objects.create(name='assembly', cv=test_cv, dbxref=test_dbxref,
                              is_obsolete=0, is_relationshiptype=0)
        test_db = Db.objects.create(name='RO')
        test_dbxref = Dbxref.objects.create(accession='00002', db=test_db)
        test_cv = Cv.objects.create(name='relationship')
        Cvterm.objects.create(
            name='contained in', cv=test_cv, dbxref=test_dbxref,
            is_obsolete=0, is_relationshiptype=0)
        test_seq_file = SequenceLoader(filename='sequence.fasta',
                                       organism='Mus musculus',
                                       soterm='assembly')
        test_seq_obj = SeqRecord(Seq('acgtgtgtgcatgctagatcgatgcatgca'),
                                 id='chr1',
                                 description='chromosome 1')
        test_seq_file.store_biopython_seq_record(test_seq_obj)
        test_feature = Feature.objects.get(uniquename='chr1')
        self.assertEqual('chromosome 1', test_feature.name)
        self.assertEqual('acgtgtgtgcatgctagatcgatgcatgca',
                         test_feature.residues)

    def test_store_biopython_seq_record_DOI(self):
        """Tests - __init__ and store_biopython_seq_record with DOI."""
        # DOI TESTING
        db2 = BibDatabase()
        db2.entries = [

                      {'journal': 'Nice Journal',
                       'comments': 'A comment',
                       'pages': '12--23',
                       'month': 'jan',
                       'abstract': 'This is an abstract. This line should be '
                                   'long enough to test multilines...',
                       'title': 'An amazing title',
                       'year': '2013',
                       'doi': '10.1186/s12864-016-2535-300002',
                       'volume': '12',
                       'ID': 'Teste2018',
                       'author': 'Foo, b. and Foo1, b. and Foo b.',
                       'keyword': 'keyword1, keyword2',
                       'ENTRYTYPE': 'article'}
                     ]
        for entry in db2.entries:
            bibtest3 = PublicationLoader(entry['ENTRYTYPE'])
            bibtest3.store_bibtex_entry(entry)
        test_bibtex3 = Pub.objects.get(uniquename='Teste2018')
        test_bibtex3_pubdbxref = PubDbxref.objects.get(pub=test_bibtex3)
        test_bibtex3_dbxref = Dbxref.objects.get(
                dbxref_id=test_bibtex3_pubdbxref.dbxref_id)
        self.assertEqual('10.1186/s12864-016-2535-300002',
                         test_bibtex3_dbxref.accession)

        Organism.objects.create(genus='Mus', species='musculus')
        test_db = Db.objects.create(name='SO')
        test_dbxref = Dbxref.objects.create(accession='00001', db=test_db)
        test_cv = Cv.objects.create(name='sequence')
        Cvterm.objects.create(name='assembly', cv=test_cv, dbxref=test_dbxref,
                              is_obsolete=0, is_relationshiptype=0)
        test_db = Db.objects.create(name='RO')
        test_dbxref = Dbxref.objects.create(accession='00002', db=test_db)
        test_cv = Cv.objects.create(name='relationship')
        Cvterm.objects.create(
            name='contained in', cv=test_cv, dbxref=test_dbxref,
            is_obsolete=0, is_relationshiptype=0)
        test_seq_file_pub = SequenceLoader(
                                       filename='sequence_doi.fasta',
                                       organism='Mus musculus',
                                       soterm='assembly',
                                       doi='10.1186/s12864-016-2535-300002')
        test_seq_obj_pub = SeqRecord(
                                 Seq('acgtgtgtgcatgctagatcgatgcatgca'),
                                 id='chr2',
                                 description='chromosome 2')
        test_seq_file_pub.store_biopython_seq_record(test_seq_obj_pub)
        test_feature_doi = Feature.objects.get(uniquename='chr2')

        self.assertEqual('chromosome 2', test_feature_doi.name)
        test_feature_pub_doi = FeaturePub.objects.get(
                pub_id=test_bibtex3.pub_id)
        test_pub_dbxref_doi = PubDbxref.objects.get(
                pub_id=test_feature_pub_doi.pub_id)
        test_dbxref_doi = Dbxref.objects.get(
                dbxref_id=test_pub_dbxref_doi.dbxref_id)
        self.assertEqual('10.1186/s12864-016-2535-300002',
                         test_dbxref_doi.accession)
