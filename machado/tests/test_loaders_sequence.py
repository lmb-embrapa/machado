# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Tests loader sequence."""

from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from bibtexparser.bibdatabase import BibDatabase
from django.core.management import call_command
from django.db.utils import IntegrityError
from django.test import TestCase

from machado.loaders.exceptions import ImportingError
from machado.loaders.publication import PublicationLoader
from machado.loaders.sequence import SequenceLoader
from machado.models import Cv, Cvterm, Db, Dbxref, Organism, Dbxrefprop
from machado.models import Feature, FeaturePub
from machado.models import Pub, PubDbxref


class SequenceTest(TestCase):
    """Tests Loaders - SequenceLoader."""

    def setUp(self):
        """Setup."""
        test_db = Db.objects.create(name="SO")
        test_dbxref = Dbxref.objects.create(accession="00001", db=test_db)
        test_cv = Cv.objects.create(name="sequence")
        Cvterm.objects.create(
            name="assembly",
            cv=test_cv,
            dbxref=test_dbxref,
            is_obsolete=0,
            is_relationshiptype=0,
        )
        test_db = Db.objects.create(name="RO")
        test_dbxref = Dbxref.objects.create(accession="00002", db=test_db)
        test_cv = Cv.objects.create(name="relationship")
        Cvterm.objects.create(
            name="contained in",
            cv=test_cv,
            dbxref=test_dbxref,
            is_obsolete=0,
            is_relationshiptype=0,
        )

    def test_fail_biopython_seq_record(self):
        """Tests fail __init__ and store_biopython_seq_record."""
        # sequence already registered
        Organism.objects.create(genus="Mus", species="musculus")
        with self.assertRaises(ImportingError):
            test_seq_file = SequenceLoader(filename="sequence.fasta")
            test_seq_obj = SeqRecord(
                Seq("acgtgtgtgcatgctagatcgatgcatgca"),
                id="chr1",
                description="chromosome 1",
            )
            test_seq_file.store_biopython_seq_record(
                test_seq_obj, "assembly", "Mus musculus"
            )
            test_seq_obj = SeqRecord(
                Seq("acgtgtgtgcatgctagatcgatgcatgca"),
                id="chr1",
                description="chromosome 1",
            )
            test_seq_file.store_biopython_seq_record(
                test_seq_obj, "assembly", "Mus musculus"
            )

    def test_store_biopython_seq_record(self):
        """Tests - __init__ and store_biopython_seq_record."""
        # test insert sequence
        Organism.objects.create(genus="Mus", species="musculus")
        test_seq_file = SequenceLoader(filename="sequence.fasta")
        test_seq_obj = SeqRecord(
            Seq("acgtgtgtgcatgctagatcgatgcatgca"), id="chr1", description="chromosome 1"
        )
        test_seq_file.store_biopython_seq_record(
            test_seq_obj, "assembly", "Mus musculus"
        )

        test_feature = Feature.objects.get(
            uniquename="chr1", organism__genus="Mus", organism__species="musculus"
        )
        self.assertEqual("chr1", test_feature.uniquename)
        self.assertEqual("chromosome 1", test_feature.name)
        self.assertEqual("acgtgtgtgcatgctagatcgatgcatgca", test_feature.residues)

        # test insert no sequence
        test_seq_obj = SeqRecord(Seq("acgtgtgtgcatgctagatcgatgcatgca"), id="chr2")
        test_seq_file.store_biopython_seq_record(
            test_seq_obj, "assembly", "Mus musculus", ignore_residues=True
        )
        test_feature = Feature.objects.get(uniquename="chr2")
        self.assertEqual("chr2", test_feature.uniquename)
        self.assertEqual("", test_feature.residues)

        # test fail insert same id, different organism
        # dbxref.accession must be unique
        Organism.objects.create(genus="Homo", species="sapiens")
        test_seq_file = SequenceLoader(filename="sequence2.fasta")
        test_seq_obj = SeqRecord(
            Seq("atgctagctagcatgactgactggtgcagtgcatgca"),
            id="chr1",
            description="chromosome 1",
        )
        with self.assertRaises(IntegrityError):
            test_seq_file.store_biopython_seq_record(
                test_seq_obj, "assembly", "Homo sapiens"
            )

    def test_store_biopython_seq_record_DOI(self):
        """Tests - __init__ and store_biopython_seq_record with DOI."""
        # DOI TESTING
        db2 = BibDatabase()
        db2.entries = [
            {
                "journal": "Nice Journal",
                "comments": "A comment",
                "pages": "12--23",
                "month": "jan",
                "abstract": "This is an abstract. This line should be "
                "long enough to test multilines...",
                "title": "An amazing title",
                "year": "2013",
                "doi": "10.1186/s12864-016-2535-300002",
                "volume": "12",
                "ID": "Teste2018",
                "author": "Foo, b. and Foo1, b. and Foo b.",
                "keyword": "keyword1, keyword2",
                "ENTRYTYPE": "article",
            }
        ]
        for entry in db2.entries:
            bibtest3 = PublicationLoader()
            bibtest3.store_bibtex_entry(entry)
        test_bibtex3 = Pub.objects.get(uniquename="Teste2018")
        test_bibtex3_pubdbxref = PubDbxref.objects.get(pub=test_bibtex3)
        test_bibtex3_dbxref = Dbxref.objects.get(
            dbxref_id=test_bibtex3_pubdbxref.dbxref_id
        )
        self.assertEqual(
            "10.1186/s12864-016-2535-300002", test_bibtex3_dbxref.accession
        )

        Organism.objects.create(genus="Mus", species="musculus")
        test_seq_file_pub = SequenceLoader(
            filename="sequence_doi.fasta", doi="10.1186/s12864-016-2535-300002"
        )
        test_seq_obj_pub = SeqRecord(
            Seq("acgtgtgtgcatgctagatcgatgcatgca"), id="chr2", description="chromosome 2"
        )
        test_seq_file_pub.store_biopython_seq_record(
            test_seq_obj_pub, "assembly", "Mus musculus"
        )

        test_feature_doi = Feature.objects.get(name="chromosome 2")

        self.assertEqual("chr2", test_feature_doi.uniquename)
        test_feature_pub_doi = FeaturePub.objects.get(pub_id=test_bibtex3.pub_id)
        test_pub_dbxref_doi = PubDbxref.objects.get(pub_id=test_feature_pub_doi.pub_id)
        test_dbxref_doi = Dbxref.objects.get(dbxref_id=test_pub_dbxref_doi.dbxref_id)
        self.assertEqual("10.1186/s12864-016-2535-300002", test_dbxref_doi.accession)
        # test remove_file
        self.assertTrue(Dbxrefprop.objects.filter(value="sequence_doi.fasta").exists())
        call_command("remove_file", "--name=sequence_doi.fasta", "--verbosity=0")
        self.assertFalse(Dbxrefprop.objects.filter(value="sequence_doi.fasta").exists())

    def test_add_sequence_to_feature(self):
        """Tests - add_sequence_to_feature."""
        # test insert sequence
        Organism.objects.create(genus="Mus", species="musculus")
        test_seq_file = SequenceLoader(filename="sequence.fasta")
        test_seq_obj = SeqRecord(
            Seq("acgtgtgtgcatgctagatcgatgcatgca"), id="chr1", description="chromosome 1"
        )
        test_seq_file.store_biopython_seq_record(
            test_seq_obj, "assembly", "Mus musculus"
        )

        # test add_sequence_to_feature
        test_seq_obj = SeqRecord(
            Seq("aaaaaaaaaaaaaaaaaaaa"), id="chr1", description="chromosome 1"
        )
        test_seq_file.add_sequence_to_feature(test_seq_obj, "assembly")
        test_feature_seq = Feature.objects.get(uniquename="chr1")
        self.assertEqual("aaaaaaaaaaaaaaaaaaaa", test_feature_seq.residues)
