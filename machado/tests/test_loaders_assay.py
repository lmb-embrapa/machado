# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Tests Assay loader."""

from django.core.management import call_command
from django.test import TestCase

from machado.loaders.assay import AssayLoader
from machado.loaders.biomaterial import BiomaterialLoader
from machado.models import Assay, AssayBiomaterial, AssayProject, Assayprop
from machado.models import Db, Dbxref, Organism, Cv, Cvterm
from machado.models import Project


class AssayTest(TestCase):
    """Tests Loaders - AssayLoader."""

    def test_store_assay(self):
        """Tests - assay."""
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
        # assay
        # will not use arraydesign nor operator
        test_filename = "test_filename.txt"
        test_assaynamedb = "SRA"
        test_assayacc = "SRR123456"
        test_assayname = test_assayacc
        test_assay_file = AssayLoader()
        test_assay = test_assay_file.store_assay(
            name=test_assayname,
            db=test_assaynamedb,
            acc=test_assayacc,
            filename=test_filename,
        )
        self.assertEqual(True, Db.objects.filter(name=test_assaynamedb).exists())
        test_db = Db.objects.get(name=test_assaynamedb)
        self.assertEqual(
            True, Dbxref.objects.filter(accession=test_assayacc, db=test_db).exists()
        )
        test_dbxref = Dbxref.objects.get(db=test_db, accession=test_assayacc)
        self.assertEqual(
            True, Assay.objects.filter(name=test_assayname, dbxref=test_dbxref).exists()
        )
        self.assertEqual(
            True,
            Assayprop.objects.filter(assay=test_assay, value=test_filename).exists(),
        )

        # assay_biomaterial
        organism_genus = "Oryza"
        organism_species = "sativa"
        # create organism
        test_organism, created = Organism.objects.get_or_create(
            genus=organism_genus, species=organism_species
        )
        test_acc = "12345"
        test_bionamedb = "GEO"
        biomaterial_name = "Title"
        test_biomaterial_file = BiomaterialLoader()
        test_biomaterial = test_biomaterial_file.store_biomaterial(
            name=biomaterial_name,
            filename=test_filename,
            organism=test_organism,
            db=test_bionamedb,
            acc=test_acc,
        )
        test_assay_file.store_assay_biomaterial(
            assay=test_assay, biomaterial=test_biomaterial, rank=0
        )
        self.assertEqual(
            True,
            AssayBiomaterial.objects.filter(
                assay=test_assay, biomaterial=test_biomaterial
            ).exists(),
        )

        # assay_project
        test_projectname = "GSE12345"
        test_project, created = Project.objects.get_or_create(name=test_projectname)
        self.assertEqual(True, Project.objects.filter(name=test_projectname).exists())
        test_assay_file.store_assay_project(assay=test_assay, project=test_project)
        self.assertEqual(
            True,
            AssayProject.objects.filter(
                assay=test_assay, project=test_project
            ).exists(),
        )
        call_command("remove_file", "--name=test_filename.txt", "--verbosity=0")
        self.assertEqual(
            False,
            Assay.objects.filter(name=test_assayname, dbxref=test_dbxref).exists(),
        )
        self.assertEqual(
            False,
            Assayprop.objects.filter(
                assay=test_assay.assay_id, value=test_filename
            ).exists(),
        )
        self.assertEqual(
            False, AssayBiomaterial.objects.filter(assay=test_assay).exists()
        )
        self.assertEqual(False, AssayProject.objects.filter(assay=test_assay).exists())
