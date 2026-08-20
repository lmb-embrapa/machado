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
from machado.management.commands.rebuild_search_index import (
    Command as RebuildCommand,
)
from machado.views.loader import COMMANDS_CONFIG


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


class RebuildSearchIndexFormOptionsTest(TestCase):
    """The registry entry for rebuild_search_index must match the command.

    The registry duplicates the command's argument names and defaults, so it
    can drift silently: it advertised batch-size default 1000 long after the
    command's default became 2000. These tests read the command's own parser
    instead of hardcoding numbers, so the next divergence fails here.

    Not every test below is a drift guard: test_unchecked_resume_sends_no_flag
    passes vacuously both before and after the registry gains a resume entry,
    so it has no power to catch registry drift specifically. It guards a
    different regression -- the shared checkbox marshalling turning an absent
    POST field into a truthy flag -- which none of the other tests cover.
    """

    def setUp(self):
        """Log in a superuser and resolve the command's argument entries."""
        self.client = Client()
        self.user = User.objects.create_superuser(
            username="rsi_admin", password="password", email="rsi@example.com"
        )
        self.client.force_login(self.user)
        self.args = COMMANDS_CONFIG["rebuild_search_index"]["args"]

    def _entry(self, name):
        """Return the registry entry for one argument name."""
        return next(arg for arg in self.args if arg["name"] == name)

    def test_batch_size_default_matches_the_command(self):
        """The registry's batch-size default is the command's own default.

        Read from the parser rather than hardcoded: hardcoding the number would
        move the drift from the registry into this test and defeat the point.
        """
        parser = RebuildCommand().create_parser("manage.py", "rebuild_search_index")
        actions = {action.dest: action for action in parser._actions}
        command_default = actions["batch_size"].default

        self.assertEqual(self._entry("batch-size")["default"], command_default)

    def test_resume_is_declared_as_a_checkbox(self):
        """Resume must be a checkbox so it marshals to a bare flag.

        Any other type produces `--resume <value>`, which argparse rejects for
        a store_true argument.
        """
        self.assertEqual(self._entry("resume")["type"], "checkbox")

    def test_form_renders_the_resume_checkbox(self):
        """The rendered form actually shows the control.

        The other tests assert on the registry and the argv; this one closes
        the gap between "declared" and "a user can see it", which is the only
        thing that would catch the template failing to render this arg type.
        """
        url = reverse(
            "loader_command_form",
            kwargs={"command_name": "rebuild_search_index"},
        )
        response = self.client.get(url)
        self.assertContains(response, 'name="resume"')
        self.assertContains(response, "Resume interrupted run")

    def test_checked_resume_becomes_a_bare_flag(self):
        """A checked resume box sends `--resume` with no following value."""
        url = reverse(
            "loader_command_form",
            kwargs={"command_name": "rebuild_search_index"},
        )

        def run_target_now(target=None, **kwargs):
            target()
            return MagicMock()

        with (
            override_settings(BASE_DIR=tempfile.gettempdir()),
            patch(
                "machado.views.loader.threading.Thread",
                side_effect=run_target_now,
            ),
            patch("machado.views.loader.subprocess.Popen") as mock_popen,
        ):
            mock_popen.return_value.pid = 1234
            mock_popen.return_value.returncode = 0
            mock_popen.return_value.communicate.return_value = ("", "")

            self.client.post(url, {"resume": "true"})

        cmd = mock_popen.call_args[0][0]
        self.assertIn("--resume", cmd)
        index = cmd.index("--resume")
        following = cmd[index + 1] if index + 1 < len(cmd) else None
        self.assertNotEqual(following, "true")

    def test_unchecked_resume_sends_no_flag(self):
        """An unchecked resume box must not put --resume on the command line."""
        url = reverse(
            "loader_command_form",
            kwargs={"command_name": "rebuild_search_index"},
        )

        def run_target_now(target=None, **kwargs):
            target()
            return MagicMock()

        with (
            override_settings(BASE_DIR=tempfile.gettempdir()),
            patch(
                "machado.views.loader.threading.Thread",
                side_effect=run_target_now,
            ),
            patch("machado.views.loader.subprocess.Popen") as mock_popen,
        ):
            mock_popen.return_value.pid = 1234
            mock_popen.return_value.returncode = 0
            mock_popen.return_value.communicate.return_value = ("", "")

            self.client.post(url, {})

        cmd = mock_popen.call_args[0][0]
        self.assertNotIn("--resume", cmd)
