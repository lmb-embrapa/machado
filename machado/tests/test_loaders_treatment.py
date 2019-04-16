# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Tests treatment loader."""

from machado.models import Biomaterial, Db, Dbxref, Organism
from machado.models import Cv, Cvterm, Treatment
from machado.loaders.treatment import TreatmentLoader
from django.test import TestCase


class TreatmentTest(TestCase):
    """Tests Loaders - TreatmentLoader."""

    def test_store_treatment(self):
        """Tests - treatment."""
        # create dummy biomaterial
        test_biomaterial, created = Biomaterial.objects.get_or_create()
        test_treatment_file = TreatmentLoader()
        # Treatment name
        treatment_name = "Title"
        test_treatment = test_treatment_file.store_treatment(
            name=treatment_name, biomaterial=test_biomaterial
        )
        self.assertEqual(
            True,
            Treatment.objects.filter(
                biomaterial=test_biomaterial, name=treatment_name
            ).exists(),
        )
