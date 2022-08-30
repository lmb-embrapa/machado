# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Tests load_publication command."""

import os

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from io import StringIO


class LoadPublicationTest(TestCase):
    """Tests Command - load_publication."""

    def call_command(self, *args, **kwargs):
        """Call command."""
        out = StringIO()
        call_command("load_publication", *args, **kwargs, stdout=out, stderr=StringIO())
        return out.getvalue()

    def test_dry_run(self):
        """Test dry run."""
        msg = "Error: the following arguments are required: --file"
        with self.assertRaisesRegexp(CommandError, msg):
            self.call_command()

    def test_insert(self):
        """Test insert."""
        directory = os.path.dirname(os.path.abspath(__file__))
        filename = os.path.join(directory, "data", "so_fake.obo")
        out = self.call_command(file=filename)
        self.assertIn("Done", out)
