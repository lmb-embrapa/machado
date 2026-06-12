# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Tests for machado.context_processors."""

import json
import tempfile
from pathlib import Path

from django.test import TestCase, RequestFactory, override_settings

from machado import context_processors


class MachadoSiteContextProcessorTest(TestCase):
    """Tests for the machado_site context processor."""

    def setUp(self):
        """Set up."""
        self.factory = RequestFactory()
        self.request = self.factory.get("/")

    def test_returns_all_expected_keys_with_defaults(self):
        """All DEFAULTS entries must be present in the returned context."""
        # Reset the release notes cache for a clean test
        context_processors._release_notes_cache = None

        ctx = context_processors.machado_site(self.request)

        for setting_name, default_value in context_processors.DEFAULTS.items():
            context_key = setting_name.lower()
            self.assertIn(context_key, ctx)
            self.assertEqual(ctx[context_key], default_value)

    @override_settings(MACHADO_SITE_TITLE="Soybean Portal")
    def test_reads_overridden_settings(self):
        """When a MACHADO_SITE_* setting is overridden, the context processor should use the overridden value."""
        ctx = context_processors.machado_site(self.request)
        self.assertEqual(ctx["machado_site_title"], "Soybean Portal")

    @override_settings(
        MACHADO_HERO_TITLE="Custom Hero",
        MACHADO_FEATURE1_TITLE="Custom Loader",
        MACHADO_STEP2_TITLE="",
    )
    def test_reads_multiple_overridden_settings(self):
        """Multiple overrides should all be reflected."""
        ctx = context_processors.machado_site(self.request)
        self.assertEqual(ctx["machado_hero_title"], "Custom Hero")
        self.assertEqual(ctx["machado_feature1_title"], "Custom Loader")
        self.assertEqual(ctx["machado_step2_title"], "")

    def test_release_notes_empty_when_no_file(self):
        """machado_release_notes should be an empty list when no file exists."""
        # Reset cache and point BASE_DIR to a temp directory with no file
        context_processors._release_notes_cache = None
        with tempfile.TemporaryDirectory() as tmpdir:
            with override_settings(BASE_DIR=Path(tmpdir)):
                # Force re-load
                context_processors._release_notes_cache = None
                ctx = context_processors.machado_site(self.request)
                self.assertEqual(ctx["machado_release_notes"], [])

    def test_release_notes_loaded_from_file(self):
        """machado_release_notes should contain parsed entries."""
        notes = [
            {
                "version": "2.0.0",
                "date": "2026-06-01",
                "description": "Major refactor.",
            },
            {
                "version": "1.0.0",
                "date": "2025-12-01",
                "description": "Initial release.",
            },
        ]
        with tempfile.TemporaryDirectory() as tmpdir:
            release_file = Path(tmpdir) / "release_notes.json"
            release_file.write_text(json.dumps(notes), encoding="utf-8")
            with override_settings(BASE_DIR=Path(tmpdir)):
                # Reset cache so it re-reads the file
                context_processors._release_notes_cache = None
                ctx = context_processors.machado_site(self.request)
                self.assertEqual(len(ctx["machado_release_notes"]), 2)
                self.assertEqual(ctx["machado_release_notes"][0]["version"], "2.0.0")
                self.assertEqual(
                    ctx["machado_release_notes"][1]["description"],
                    "Initial release.",
                )

    def test_malformed_json_returns_empty_list(self):
        """Malformed JSON should log a warning and return an empty list."""
        with tempfile.TemporaryDirectory() as tmpdir:
            release_file = Path(tmpdir) / "release_notes.json"
            release_file.write_text("NOT VALID JSON {{{", encoding="utf-8")
            with override_settings(BASE_DIR=Path(tmpdir)):
                context_processors._release_notes_cache = None
                with self.assertLogs("machado.context_processors", level="WARNING") as cm:
                    ctx = context_processors.machado_site(self.request)
                self.assertEqual(ctx["machado_release_notes"], [])
                self.assertTrue(any("Failed to load release_notes.json" in log for log in cm.output))

    def test_json_not_array_returns_empty_list(self):
        """If the JSON is valid but not an array, return empty list."""
        with tempfile.TemporaryDirectory() as tmpdir:
            release_file = Path(tmpdir) / "release_notes.json"
            release_file.write_text('{"not": "an array"}', encoding="utf-8")
            with override_settings(BASE_DIR=Path(tmpdir)):
                context_processors._release_notes_cache = None
                with self.assertLogs("machado.context_processors", level="WARNING") as cm:
                    ctx = context_processors.machado_site(self.request)
                self.assertEqual(ctx["machado_release_notes"], [])
                self.assertTrue(any("expected a JSON array" in log for log in cm.output))

    def test_release_notes_empty_when_no_base_dir(self):
        """When BASE_DIR is not set, release notes should be empty."""
        context_processors._release_notes_cache = None
        # Temporarily remove BASE_DIR from settings
        from django.conf import settings as django_settings

        original = getattr(django_settings, "BASE_DIR", None)
        had_attr = hasattr(django_settings, "BASE_DIR")
        if had_attr:
            delattr(django_settings, "BASE_DIR")
        try:
            result = context_processors._load_release_notes()
            self.assertEqual(result, [])
        finally:
            if had_attr and original is not None:
                django_settings.BASE_DIR = original

    def tearDown(self):
        """Tear down."""
        # Always reset the cache after each test to avoid test pollution
        context_processors._release_notes_cache = None
