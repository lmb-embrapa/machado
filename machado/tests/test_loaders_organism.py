# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Tests organism loader."""

from machado.loaders.organism import OrganismLoader
from machado.models import Db, Dbxref, Organism, OrganismDbxref, Organismprop
from django.test import TestCase
from django.core.management import call_command


class OrganismTest(TestCase):
    """Tests Loaders - OrganismLoader."""

    def test_store_organism_record(self):
        """Tests - __init__ and store_organism_record."""
        # new organism loader
        organism_db = OrganismLoader('test organism loader')
        test_db = Db.objects.get(name='test organism loader')

        taxid = 185542
        scname = 'Ilex paraguariensis'
        common_names = ['mate', 'Brazilian-tea', 'yerba-mate']
        synonyms = ['Ilex paraguensis']

        organism_db.store_organism_record(taxid=taxid,
                                          scname=scname,
                                          common_names=common_names,
                                          synonyms=synonyms)

        test_dbxref = Dbxref.objects.get(db=test_db, accession='185542')
        test_organism_dbxref = OrganismDbxref.objects.get(
            dbxref=test_dbxref)
        test = Organism.objects.get(
            organism_id=test_organism_dbxref.organism_id)
        test_synonym = Organismprop.objects.filter(
            organism_id=test_organism_dbxref.organism_id)
        self.assertEqual('Ilex', test.genus)
        self.assertEqual('paraguariensis', test.species)
        self.assertEqual('mate,Brazilian-tea,yerba-mate', test.common_name)
        self.assertEqual('Ilex paraguensis', test_synonym[0].value)
        # test remove_organism
        self.assertTrue(Organism.objects.filter(genus='Ilex',
                                                species='paraguariensis')
                        .exists())
        call_command("remove_organism",
                     "--genus=Ilex",
                     "--species=paraguariensis",
                     "--verbosity=0")
        self.assertFalse(Organism.objects.filter(genus='Ilex',
                                                 species='paraguariensis')
                         .exists())
