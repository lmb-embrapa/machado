# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Tests Models."""

from django.test import TestCase

from machado.models import Db, Dbxref, Cvterm, Cv, Pub, PubDbxref


class DbModelTest(TestCase):
    """Tests Models - DB."""

    def test_DB(self):
        """Tests - DB."""
        test_db = Db.objects.create(
            name="test_name",
            description="test_description",
            urlprefix="test_urlprefix",
            url="test_url",
        )
        self.assertEqual("test_name", test_db.name)

    def test_PUB(self):
        """Tests - Publication."""
        test_db_pub, created = Db.objects.get_or_create(name="internal")
        test_dbxref, created = Dbxref.objects.get_or_create(
            accession="article", db=test_db_pub
        )
        test_cv, created = Cv.objects.get_or_create(name="null")
        test_cvterm, created = Cvterm.objects.get_or_create(
            name="article",
            cv=test_cv,
            dbxref=test_dbxref,
            is_obsolete=0,
            is_relationshiptype=0,
        )
        # create test pub entry
        # ommited 'volume' just to test null values
        test_pub = Pub.objects.create(
            type=test_cvterm,
            uniquename="Test2018",
            title="Test Title",
            pyear="2018",
            pages="2000",
            series_name="Journal of Testing",
        )
        test_doi = "10.1111/t12121-013-1415-6"
        test_db_doi = Db.objects.create(name="doi")
        test_dbxref_doi = Dbxref.objects.create(accession=test_doi, db=test_db_doi)
        PubDbxref.objects.create(pub=test_pub, dbxref=test_dbxref_doi, is_current=True)

        pub_test = Pub.objects.get(uniquename="Test2018")
        self.assertEqual("2018", pub_test.pyear)
        self.assertEqual("10.1111/t12121-013-1415-6", test_dbxref_doi.accession)

        test_entry = dict()
        test_entry["ID"] = "Chado2003"
        test_entry["title"] = "A mock test title"
        test_entry["year"] = "2003"
        test_entry["pages"] = "2000"
        test_entry["doi"] = "10.1111/s12122-012-1313-4"
        test_entry["journal"] = "Journal of Testing"
        # 'volume' information not declared: test get null value
        test_pub2 = Pub.objects.create(
            type=test_cvterm,
            uniquename=test_entry["ID"],
            title=test_entry["title"],
            pyear=test_entry["year"],
            pages=test_entry["pages"],
            volume=test_entry.get("volume"),
        )
        test_dbxref_doi2 = Dbxref.objects.create(
            accession=test_entry["doi"], db=test_db_doi
        )
        PubDbxref.objects.create(
            pub=test_pub2, dbxref=test_dbxref_doi2, is_current=True
        )
        self.assertEqual("2003", test_pub2.pyear)
