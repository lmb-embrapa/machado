# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Tests load_fasta command."""

import os

from django.apps import apps
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TransactionTestCase
from io import StringIO
from machado.models import Db, Dbxref, Cv, Cvterm, Organism
from machado.loaders.common import retrieve_organism

# Configures tqdm to not show the progress bar
from tqdm import tqdm
from functools import partialmethod

tqdm.__init__ = partialmethod(tqdm.__init__, disable=True)


# Configures TransactionTestCase to be able to flush data between tests
TransactionTestCase.available_apps = {
    app_config.name for app_config in apps.get_app_configs()
}


class LoadFastaTest(TransactionTestCase):
    """Tests Command - load_fasta."""

    TransactionTestCase.available_apps = {
        app_config.name for app_config in apps.get_app_configs()
    }

    def setUp(self):
        """Set up."""
        test_db, created = Db.objects.get_or_create(name="SO")
        test_dbxref, created = Dbxref.objects.get_or_create(
            accession="00001",
            db=test_db,
        )
        test_cv, created = Cv.objects.get_or_create(name="sequence")
        Cvterm.objects.get_or_create(
            name="chromosome",
            cv=test_cv,
            dbxref=test_dbxref,
            is_obsolete=0,
            is_relationshiptype=0,
        )

        test_db, created = Db.objects.get_or_create(name="RO")
        test_dbxref, created = Dbxref.objects.get_or_create(
            accession="00002",
            db=test_db,
        )
        test_cv, created = Cv.objects.get_or_create(name="relationship")
        Cvterm.objects.get_or_create(
            name="contained in",
            cv=test_cv,
            dbxref=test_dbxref,
            is_obsolete=0,
            is_relationshiptype=0,
        )

        Organism.objects.get_or_create(
            genus="Arabidopsis",
            species="thaliana",
        )

    def call_command(self, *args, **kwargs):
        """Call command."""
        out = StringIO()
        call_command("load_fasta", *args, **kwargs, stdout=out, stderr=StringIO())
        return out.getvalue()

    def test_dry_run(self):
        """Test dry run."""
        msg = "Error: the following arguments are required: --file"
        with self.assertRaisesRegexp(CommandError, msg):
            self.call_command()

    def test_insert(self):
        """Test insert."""
        #        call_command("insert_organism", genus="Arabidopsis", species="thaliana")
        organism_obj = retrieve_organism("Arabidopsis thaliana")
        self.assertEqual(organism_obj.genus, "Arabidopsis")

        directory = os.path.dirname(os.path.abspath(__file__))
        filename = os.path.join(directory, "data", "Athaliana_167_TAIR9.fa")
        out = self.call_command(
            soterm="chromosome",
            organism="Arabidopsis thaliana",
            file=filename,
        )
        self.assertIn("Done", out)
