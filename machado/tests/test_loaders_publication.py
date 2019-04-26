# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Tests publicationtion loader."""

from bibtexparser.bibdatabase import BibDatabase
from django.core.management import call_command
from django.test import TestCase

from machado.loaders.publication import PublicationLoader
from machado.models import Pub, Dbxref, PubDbxref


class PublicationTest(TestCase):
    """Tests Loaders - PublicationLoader."""

    def test_store_pub_record(self):
        """Tests - __init__ and store_pub_record."""
        # test PublicationLoader
        test_entry2 = dict()
        test_entry2["ENTRYTYPE"] = "article"
        test_entry2["ID"] = "Chado2006"
        test_entry2["title"] = "A mock test title"
        test_entry2["year"] = "2006"
        test_entry2["pages"] = "12000"
        test_entry2["doi"] = "10.1111/s12122-012-1313-4"
        test_entry2["author"] = "Foo, b. and Foo1, b. and Foo b."
        test_entry2["volume"] = "v2"
        test_entry2["journal"] = "Journal of Testing"
        bibtest = PublicationLoader()
        bibtest.store_bibtex_entry(test_entry2)
        test_bibtex = Pub.objects.get(uniquename="Chado2006")
        self.assertEqual("v2", test_bibtex.volume)
        # test mock bibtexparser object database'
        db = BibDatabase()
        # pages ommited
        db.entries = [
            {
                "journal": "Nice Journal",
                "comments": "A comment",
                "month": "jan",
                "abstract": "This is an abstract. This line should be "
                "long enough to test multilines...",
                "title": "An amazing title",
                "year": "2013",
                "doi": "10.1111/s12122-012-1313-5",
                "volume": "12",
                "ID": "Cesar2013",
                "author": "Foo, b. and Foo1, b. and Foo b.",
                "keyword": "keyword1, keyword2",
                "ENTRYTYPE": "article",
            }
        ]
        for entry in db.entries:
            bibtest2 = PublicationLoader()
            bibtest2.store_bibtex_entry(entry)
        test_bibtex2 = Pub.objects.get(uniquename="Cesar2013")
        self.assertEqual("12", test_bibtex2.volume)
        self.assertEqual(None, test_bibtex2.pages)
        test_bibtex2_pub_dbxref = PubDbxref.objects.get(pub_id=test_bibtex2.pub_id)
        self.assertEqual(test_bibtex2.pub_id, test_bibtex2_pub_dbxref.pub_id)
        # test remove publication (with cascade enabled)
        self.assertTrue(Pub.objects.filter(uniquename="Cesar2013").exists())
        call_command(
            "remove_publication", "--doi=10.1111/s12122-012-1313-5", "--verbosity=0"
        )
        self.assertFalse(Pub.objects.filter(uniquename="Cesar2013").exists())
        # check if dbxref remains
        self.assertTrue(
            Dbxref.objects.filter(accession="10.1111/s12122-012-1313-5").exists()
        )
