# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Tests project loader."""

from django.core.management import call_command
from django.test import TestCase

from machado.loaders.project import ProjectLoader
from machado.models import Cv, Cvterm
from machado.models import Db, Dbxref
from machado.models import Project, Projectprop


class ProjectTest(TestCase):
    """Tests Loaders - ProjectLoader."""

    def test_store_project(self):
        """Tests - project."""
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
        test_project_file1 = ProjectLoader()
        # Project name
        test_filename = "test_filename.txt"
        test_acc = "GSE12345"
        test_project1 = test_project_file1.store_project(
            name=test_acc, filename=test_filename
        )
        self.assertEqual(test_acc, test_project1.name)
        self.assertEqual(
            True, Project.objects.filter(project_id=test_project1.project_id).exists()
        )
        self.assertEqual(
            True,
            Projectprop.objects.filter(
                project=test_project1, value=test_filename
            ).exists(),
        )
        # ProjectDbxref with known accession and Db
        call_command("remove_file", "--name=test_filename.txt", "--verbosity=0")
        self.assertEqual(
            False, Project.objects.filter(project_id=test_project1.project_id).exists()
        )
        # self.assertFalse(test_acc, test_dbxref1.accession)
        self.assertEqual(
            False,
            Projectprop.objects.filter(
                project_id=test_project1.project_id, value=test_filename
            ).exists(),
        )
