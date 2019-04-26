# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Tests biomaterial loader."""

from django.core.management import call_command
from django.test import TestCase

from machado.loaders.biomaterial import BiomaterialLoader
from machado.loaders.treatment import TreatmentLoader
from machado.models import Biomaterial, Db, Dbxref, Organism
from machado.models import Cv, Cvterm, BiomaterialTreatment, Biomaterialprop


class BiomaterialTest(TestCase):
    """Tests Loaders - BiomaterialLoader."""

    def test_store_biomaterial(self):
        """Tests - biomaterial."""
        test_db = Db.objects.create(name="RO")
        test_dbxref = Dbxref.objects.create(accession="00002", db=test_db)
        test_cv = Cv.objects.create(name="relationship")
        Cvterm.objects.create(
            name="contained in",
            cv=test_cv,
            dbxref=test_dbxref,
            is_obsolete=0,
            is_relationshiptype=0,
        )
        test_db = Db.objects.create(name="SO")
        test_dbxref = Dbxref.objects.create(accession="12345", db=test_db)
        test_cv = Cv.objects.create(name="sequence")
        Cvterm.objects.create(
            name="polypeptide",
            cv=test_cv,
            dbxref=test_dbxref,
            is_obsolete=0,
            is_relationshiptype=0,
        )
        organism_genus = "Oryza"
        organism_species = "sativa"
        # create organism
        test_organism, created = Organism.objects.get_or_create(
            genus=organism_genus, species=organism_species
        )
        test_filename = "test_filename.txt"
        test_acc = "12345"
        test_namedb = "GEO"
        biomaterial_name = "Title"
        test_biomaterial_file = BiomaterialLoader()
        test_biomaterial = test_biomaterial_file.store_biomaterial(
            name=biomaterial_name,
            filename=test_filename,
            organism=test_organism,
            db=test_namedb,
            acc=test_acc,
        )
        self.assertEqual(True, Db.objects.filter(name=test_namedb).exists())
        test_db = Db.objects.get(name=test_namedb)
        self.assertEqual(
            True, Dbxref.objects.filter(db=test_db, accession=test_acc).exists()
        )
        test_dbxref = Dbxref.objects.get(db=test_db, accession=test_acc)
        self.assertEqual(
            True,
            Biomaterial.objects.filter(
                taxon_id=test_organism.organism_id,
                name=biomaterial_name,
                dbxref=test_dbxref,
            ).exists(),
        )
        self.assertEqual(
            True,
            Biomaterialprop.objects.filter(
                biomaterial=test_biomaterial, value=test_filename
            ).exists(),
        )
        # biomaterial_treatment
        test_treatment_file = TreatmentLoader()
        # Treatment name
        treatment_name = "Title"
        test_treatment = test_treatment_file.store_treatment(
            name=treatment_name, biomaterial=test_biomaterial
        )
        test_biomaterial_file.store_biomaterial_treatment(
            biomaterial=test_biomaterial, treatment=test_treatment, rank=0
        )
        self.assertEqual(
            True,
            BiomaterialTreatment.objects.filter(
                biomaterial=test_biomaterial, treatment=test_treatment
            ).exists(),
        )
        call_command("remove_file", "--name=test_filename.txt", "--verbosity=0")
        self.assertEqual(
            False,
            Biomaterial.objects.filter(
                taxon_id=test_organism.organism_id,
                name=biomaterial_name,
                dbxref=test_dbxref,
            ).exists(),
        )
        self.assertEqual(
            False,
            Biomaterialprop.objects.filter(
                biomaterial=test_biomaterial, value=test_filename
            ).exists(),
        )
        self.assertEqual(
            False,
            BiomaterialTreatment.objects.filter(
                biomaterial=test_biomaterial, treatment=test_treatment
            ).exists(),
        )
