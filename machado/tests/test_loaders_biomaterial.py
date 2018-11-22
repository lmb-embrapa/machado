# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Tests biomaterial loader."""

from machado.models import Biomaterial, Db, Dbxref, Organism
from machado.models import Cv, Cvterm, Treatment, BiomaterialTreatment
from machado.loaders.common import insert_organism
from machado.loaders.biomaterial import BiomaterialLoader
from machado.loaders.treatment import TreatmentLoader
from django.test import TestCase

class BiomaterialTest(TestCase):
    """Tests Loaders - BiomaterialLoader."""

    def test_store_biomaterial(self):
        """Tests - biomaterial."""
        organism_genus = "Oryza"
        organism_species = "sativa"
        # create organism
        test_organism, created = Organism.objects.get_or_create(
                genus=organism_genus,
                species=organism_species)
        test_acc = "12345"
        test_namedb = "GEO"
        biomaterial_name = "Title"
        test_biomaterial_file = BiomaterialLoader()
        test_biomaterial = test_biomaterial_file.store_biomaterial(
                name=biomaterial_name,
                organism=test_organism,
                db=test_namedb,
                acc=test_acc)
        self.assertEqual(True, Db.objects.filter(
            name=test_namedb,
            ).exists())
        test_db = Db.objects.get(name=test_namedb)
        self.assertEqual(True, Dbxref.objects.filter(
            db=test_db, accession=test_acc
            ).exists())
        test_dbxref = Dbxref.objects.get(db=test_db, accession=test_acc)
        self.assertEqual(True, Biomaterial.objects.filter(
            taxon_id=test_organism.organism_id,
            name=biomaterial_name,
            dbxref=test_dbxref
            ).exists())

        # biomaterial_treatment
        test_treatment_file = TreatmentLoader()
        # Treatment name
        treatment_name = "Title"
        test_treatment = test_treatment_file.store_treatment(
                name=treatment_name,
                biomaterial=test_biomaterial)
        test_biomaterial_file.store_biomaterial_treatment(
                biomaterial=test_biomaterial,
                treatment=test_treatment,
                rank=0)
        self.assertEqual(True, BiomaterialTreatment.objects.filter(
            biomaterial=test_biomaterial,
            treatment=test_treatment
            ).exists())

