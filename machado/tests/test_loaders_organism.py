# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Tests organism loader."""

from bibtexparser.bibdatabase import BibDatabase
from django.core.management import call_command
from django.test import TestCase

from machado.loaders.organism import OrganismLoader
from machado.loaders.publication import PublicationLoader
from machado.models import Db, Dbxref
from machado.models import Organism, OrganismDbxref, Organismprop, OrganismPub


class OrganismTest(TestCase):
    """Tests Loaders - OrganismLoader."""

    def test_store_organism_record(self):
        """Tests - __init__ and store_organism_record."""
        # new organism loader
        organism_db = OrganismLoader("test organism loader")
        test_db = Db.objects.get(name="test organism loader")

        taxid = 185542
        scname = "Ilex paraguariensis"
        common_names = ["mate", "Brazilian-tea", "yerba-mate"]
        synonyms = ["Ilex paraguensis"]

        organism_db.store_organism_record(
            taxid=taxid, scname=scname, common_names=common_names, synonyms=synonyms
        )

        test_dbxref = Dbxref.objects.get(db=test_db, accession="185542")
        test_organism_dbxref = OrganismDbxref.objects.get(dbxref=test_dbxref)
        test = Organism.objects.get(organism_id=test_organism_dbxref.organism_id)
        test_synonym = Organismprop.objects.filter(
            organism_id=test_organism_dbxref.organism_id
        )
        self.assertEqual("Ilex", test.genus)
        self.assertEqual("paraguariensis", test.species)
        self.assertEqual("mate,Brazilian-tea,yerba-mate", test.common_name)
        self.assertEqual("Ilex paraguensis", test_synonym[0].value)
        # test remove_organism
        self.assertTrue(
            Organism.objects.filter(genus="Ilex", species="paraguariensis").exists()
        )
        call_command(
            "remove_organism",
            "--genus=Ilex",
            "--species=paraguariensis",
            "--verbosity=0",
        )
        self.assertFalse(
            Organism.objects.filter(genus="Ilex", species="paraguariensis").exists()
        )

    def test_store_organism_publication(self):
        """Tests - store organism publication."""
        test_organism = Organism.objects.create(genus="Mus", species="musculus")

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
            bibtest = PublicationLoader()
            bibtest.store_bibtex_entry(entry)

        OrganismLoader().store_organism_publication(
            organism="Mus musculus", doi="10.1186/s12864-016-2535-300002"
        )
        test_organismpub = OrganismPub.objects.get(organism=test_organism)
        self.assertEqual("An amazing title", test_organismpub.pub.title)
