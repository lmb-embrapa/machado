# Copyright 2026 by Embrapa. All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

import tempfile
from unittest.mock import patch, MagicMock

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client, override_settings
from django.contrib.auth.models import User
from django.urls import reverse
from machado.models import Db, Dbxref


class LoaderViewsTest(TestCase):
    """Test loader views functionality."""

    def setUp(self):
        """Set up test user and sample DOI dbxref database records."""
        self.client = Client()
        self.user = User.objects.create_superuser(
            username="admin", password="password", email="admin@example.com"
        )
        self.client.force_login(self.user)
        self.doi_db = Db.objects.create(name="DOI")
        self.dbxref1 = Dbxref.objects.create(
            accession="10.1234/test.doi.1", db=self.doi_db
        )
        self.dbxref2 = Dbxref.objects.create(
            accession="10.1234/test.doi.2", db=self.doi_db
        )

    def test_command_form_doi_dropdown(self):
        """Test dynamic DOI choices are correctly populated in dropdowns."""
        url = reverse("loader_command_form", kwargs={"command_name": "load_fasta"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # Check that the option elements for the DOIs are rendered in the HTML
        self.assertContains(
            response, '<option value="10.1234/test.doi.1">10.1234/test.doi.1</option>'
        )
        self.assertContains(
            response, '<option value="10.1234/test.doi.2">10.1234/test.doi.2</option>'
        )

    def test_command_form_format_choices(self):
        """Test similarity format static options dropdown is correctly populated."""
        url = reverse("loader_command_form", kwargs={"command_name": "load_similarity"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # Check that the format choices are rendered in the HTML
        self.assertContains(response, '<option value="blast-xml">blast-xml</option>')
        self.assertContains(
            response, '<option value="interproscan-xml">interproscan-xml</option>'
        )

    def test_load_fasta_checkbox_nosequence_sent_as_flag(self):
        """Regression: a checked 'nosequence' checkbox must become a bare
        --nosequence flag, not '--nosequence true', which argparse rejects
        for a store_true argument."""
        url = reverse("loader_command_form", kwargs={"command_name": "load_fasta"})
        data = {
            "file_upload": SimpleUploadedFile("test.fasta", b">seq1\nACGT\n"),
            "organism": "999999",
            "soterm": "999999",
            "nosequence": "true",
        }

        def run_target_now(target=None, **kwargs):
            target()
            return MagicMock()

        with (
            override_settings(BASE_DIR=tempfile.gettempdir()),
            patch("machado.views.loader.threading.Thread", side_effect=run_target_now),
            patch("machado.views.loader.subprocess.Popen") as mock_popen,
        ):
            mock_popen.return_value.pid = 1234
            mock_popen.return_value.returncode = 0
            mock_popen.return_value.communicate.return_value = ("", "")

            self.client.post(url, data)

        cmd = mock_popen.call_args[0][0]
        self.assertIn("--nosequence", cmd)
        idx = cmd.index("--nosequence")
        next_token = cmd[idx + 1] if idx + 1 < len(cmd) else None
        self.assertNotEqual(next_token, "true")
