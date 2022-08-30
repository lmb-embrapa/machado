# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Tests insert_organism command."""

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from io import StringIO


class InsertOrganismTest(TestCase):
    """Tests Command - insert_organism."""

    def call_command(self, *args, **kwargs):
        """Call command."""
        out = StringIO()
        call_command("insert_organism", *args, **kwargs, stdout=out, stderr=StringIO())
        return out.getvalue()

    def test_dry_run(self):
        """Test dry run."""
        msg = "Error: the following arguments are required: --genus, --species"
        with self.assertRaisesRegexp(CommandError, msg):
            self.call_command()

    def test_insert(self):
        """Test insert."""
        out = self.call_command(genus="Arabidopsis", species="thaliana")
        self.assertIn("Arabidopsis thaliana registered", out)
