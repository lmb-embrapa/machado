# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Tests command load relations ontology."""

import os
from django.test import TestCase
from django.core.exceptions import ObjectDoesNotExist
from django.core.management import call_command
from django.core.management.base import CommandError
from machado.models import Cvterm


class CommandTest(TestCase):
    """Tests Loaders - OntologyLoader."""

    def test_load_relations_ontology(self):
        """Tests - load relations ontology."""
        # test load relations ontology
        directory = os.path.dirname(os.path.abspath(__file__))
        file = os.path.join(directory, 'data', 'ro_trunc.obo')
        call_command("load_relations_ontology",
                     "--file={}".format(file),
                     "--verbosity=0")
        self.assertTrue(Cvterm.objects.get(name='overlaps'))

        # test ImportingError
        with self.assertRaises(CommandError):
            call_command("load_relations_ontology",
                         "--file=does_not_exist")

        # test remove relations ontology
        call_command("remove_ontology",
                     "--name=relationship",
                     "--verbosity=0")
        with self.assertRaises(ObjectDoesNotExist):
            Cvterm.objects.get(name='gene')

        # test remove ontology does not exist
        with self.assertRaisesMessage(
                    CommandError,
                    'Cannot remove \'relationship\' (not registered)'):
            call_command("remove_ontology",
                         "--name=relationship",
                         "--verbosity=0")
