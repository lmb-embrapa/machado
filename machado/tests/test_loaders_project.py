# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Tests project loader."""

from machado.models import Db, Dbxref
from machado.models import ProjectDbxref
from machado.loaders.project import ProjectLoader
from django.test import TestCase


class ProjectTest(TestCase):
    """Tests Loaders - ProjectLoader."""

    def test_store_project(self):
        """Tests - project."""
        test_project_file1 = ProjectLoader()
        # Project name
        test_name = "Title"
        test_project1 = test_project_file1.store_project(name=test_name)
        self.assertEqual('Title', test_project1.name)
        # ProjectDbxref with known accession and Db
        test_acc = "12345"
        test_namedb = "GEO"
        test_project_file1.store_project_dbxref(project=test_project1,
                                                acc=test_acc,
                                                db=test_namedb)
        test_db1 = Db.objects.get(name=test_namedb)
        self.assertEqual(True, Dbxref.objects.filter(
            accession=test_acc, db=test_db1).exists())
        test_dbxref1 = Dbxref.objects.get(accession=test_acc, db=test_db1)
        self.assertEqual(test_acc, test_dbxref1.accession)
        self.assertEqual(True, ProjectDbxref.objects.filter(
            project=test_project1, dbxref=test_dbxref1).exists())
