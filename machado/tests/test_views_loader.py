# Copyright 2026 by Embrapa. All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from machado.models import Db, Dbxref

class LoaderViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_superuser(username="admin", password="password", email="admin@example.com")
        self.client.force_login(self.user)
        self.doi_db = Db.objects.create(name="DOI")
        self.dbxref1 = Dbxref.objects.create(accession="10.1234/test.doi.1", db=self.doi_db)
        self.dbxref2 = Dbxref.objects.create(accession="10.1234/test.doi.2", db=self.doi_db)

    def test_command_form_doi_dropdown(self):
        url = reverse("loader_command_form", kwargs={"command_name": "load_fasta"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # Check that the option elements for the DOIs are rendered in the HTML
        self.assertContains(response, '<option value="10.1234/test.doi.1">10.1234/test.doi.1</option>')
        self.assertContains(response, '<option value="10.1234/test.doi.2">10.1234/test.doi.2</option>')

    def test_command_form_format_choices(self):
        url = reverse("loader_command_form", kwargs={"command_name": "load_similarity"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # Check that the format choices are rendered in the HTML
        self.assertContains(response, '<option value="blast-xml">blast-xml</option>')
        self.assertContains(response, '<option value="interproscan-xml">interproscan-xml</option>')
