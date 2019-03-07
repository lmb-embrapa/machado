# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Tests loader sequence."""

from django.test import TestCase
from django.core.exceptions import ObjectDoesNotExist
from django.core.management import call_command
from django.core.management.base import CommandError
from machado.models import Organism


class CommandTest(TestCase):
    """Tests Loaders - SequenceLoader."""

    def test_insert_organism(self):
        """Tests - insert organism."""
        # test insert organism
        call_command("insert_organism",
                     "--genus=Mus",
                     "--species=musculus",
                     "--verbosity=0")
        self.assertTrue(Organism.objects.get(genus='Mus', species='musculus'))

        # test insert organism full
        call_command("insert_organism",
                     "--genus=Escherichia",
                     "--species=coli",
                     "--abbreviation=E.coli",
                     "--common_name=E.coli",
                     "--infraspecific_name=spp.",
                     "--comment=Escherichia coli",
                     "--verbosity=0")
        self.assertTrue(Organism.objects.get(genus='Escherichia',
                                             species='coli',
                                             abbreviation='E.coli',
                                             common_name='E.coli',
                                             infraspecific_name='spp.',
                                             comment='Escherichia coli'))

        # test insert duplicate organism
        with self.assertRaisesMessage(
                CommandError, 'Organism already registered (Mus musculus)!'):
            call_command("insert_organism",
                         "--genus=Mus",
                         "--species=musculus")

        # test remove organism
        call_command("remove_organism",
                     "--genus=Mus",
                     "--species=musculus",
                     "--verbosity=0")
        with self.assertRaises(ObjectDoesNotExist):
            Organism.objects.get(genus='Mus', species='musculus')

        # test remove organism does not exist
        with self.assertRaisesMessage(
                CommandError, 'Organism does not exist in database!'):
            call_command("remove_organism",
                         "--genus=Not",
                         "--species=Registered",
                         "--verbosity=0")
