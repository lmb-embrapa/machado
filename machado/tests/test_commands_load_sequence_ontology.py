# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Tests command load sequence ontology."""

import os
from django.test import TestCase
from django.core.management import call_command
from django.core.management.base import CommandError
from machado.models import Cvterm


class CommandTest(TestCase):
    """Tests Loaders - SequenceLoader."""

    def test_insert_organism(self):
        """Tests - insert organism."""
        # test insert organism
        directory = os.path.dirname(os.path.abspath(__file__))
        file = os.path.join(directory, 'data', 'so_trunc.obo')
        call_command("load_sequence_ontology",
                     "--file={}".format(file),
                     "--verbosity=0")
        self.assertTrue(Cvterm.objects.get(name='gene'))

        # test ImportingError
        with self.assertRaises(CommandError):
            call_command("load_sequence_ontology",
                         "--file=does_not_exist")
