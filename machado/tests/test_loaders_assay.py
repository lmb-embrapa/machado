# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Tests Assay loader."""

from machado.models import Assay, AssayBiomaterial, AssayProject, Biomaterial
from machado.models import Db, Dbxref, Organism, Contact, Arraydesign
from machado.models import Cv, Cvterm, Treatment, Project
from machado.loaders.common import insert_organism
from machado.loaders.assay import AssayLoader
from machado.loaders.biomaterial import BiomaterialLoader
from machado.loaders.project import ProjectLoader
from django.test import TestCase
from datetime import datetime

class AssayTest(TestCase):
    """Tests Loaders - AssayLoader."""

    def test_store_assay(self):
        """Tests - assay."""
        # assay
        # will not use arraydesign nor operator
        test_assaydate = 'Oct-16-2016'
        test_assaynamedb = "SRA"
        test_assayacc = "SRR123456"
        test_assayname = test_assayacc
        test_assay_file = AssayLoader()
        test_assay = test_assay_file.store_assay(
                name=test_assayname,
                db=test_assaynamedb,
                acc=test_assayacc,
                assaydate=test_assaydate
                )
        self.assertEqual(True, Db.objects.filter(
            name=test_assaynamedb
            ).exists())
        test_db = Db.objects.get(name=test_assaynamedb)
        self.assertEqual(True, Dbxref.objects.filter(
            accession=test_assayacc,
            db=test_db
            ).exists())
        test_dbxref = Dbxref.objects.get(db=test_db, accession=test_assayacc)
        date_format = '%b-%d-%Y'
        test_assaydate_format = datetime.strptime(test_assaydate, date_format)
        self.assertEqual(True, Assay.objects.filter(
            assaydate=test_assaydate_format,
            name=test_assayname,
            dbxref=test_dbxref
            ).exists())

        # assay_biomaterial
        organism_genus = "Oryza"
        organism_species = "sativa"
        # create organism
        test_organism, created = Organism.objects.get_or_create(
                genus=organism_genus,
                species=organism_species)
        test_acc = "12345"
        test_bionamedb = "GEO"
        biomaterial_name = "Title"
        test_biomaterial_file = BiomaterialLoader()
        test_biomaterial = test_biomaterial_file.store_biomaterial(
                name=biomaterial_name,
                organism=test_organism,
                db=test_bionamedb,
                acc=test_acc)
        test_assay_file.store_assay_biomaterial(
                assay=test_assay,
                biomaterial=test_biomaterial,
                rank=0)
        self.assertEqual(True, AssayBiomaterial.objects.filter(
            assay=test_assay,
            biomaterial=test_biomaterial
            ).exists())

        # assay_project
        test_projectname = "Title"
        test_project, created = Project.objects.get_or_create(
                name=test_projectname)
        test_assay_file.store_assay_project(
                assay=test_assay,
                project=test_project)
        self.assertEqual(True, AssayProject.objects.filter(
            assay=test_assay,
            project=test_project
            ).exists())

