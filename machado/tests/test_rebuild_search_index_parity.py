# Copyright 2026 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Output-parity tests for rebuild_search_index.

These lock in the index contents produced by the command so the batched
rewrite can be verified to change performance without changing output.
"""

import json
from pathlib import Path

from django.core.management import call_command
from django.test import TestCase

from machado.models import FeatureSearchIndex
from machado.tests.searchindex_fixture import (
    build_search_index_fixture,
    snapshot_index,
)

SNAPSHOT_PATH = Path(__file__).parent / "data" / "search_index_snapshot.json"


class RebuildSearchIndexParityTest(TestCase):
    """The command's output must match the recorded snapshot exactly."""

    def setUp(self):
        """Build the shared fixture corpus."""
        build_search_index_fixture()

    def test_index_matches_snapshot(self):
        """Running the command reproduces the recorded index contents."""
        call_command("rebuild_search_index", batch_size=2, verbosity=0)
        actual = snapshot_index()

        if not SNAPSHOT_PATH.exists():
            SNAPSHOT_PATH.parent.mkdir(parents=True, exist_ok=True)
            SNAPSHOT_PATH.write_text(json.dumps(actual, indent=2, sort_keys=True))
            self.fail(
                f"Snapshot did not exist; wrote it to {SNAPSHOT_PATH}. "
                "Inspect it for correctness, commit it, then re-run."
            )

        expected = json.loads(SNAPSHOT_PATH.read_text())
        self.assertEqual(
            actual,
            expected,
            "index output drifted from the recorded snapshot",
        )

    def test_every_valid_feature_is_indexed(self):
        """Only sequence-CV features of a valid type are indexed."""
        # NOTE: the brief's verbatim version of this test omitted this call,
        # which left it checking an always-empty table (each test method
        # gets its own isolated transaction, so nothing from
        # test_index_matches_snapshot carries over). Added so the
        # assertions below actually exercise the command.
        call_command("rebuild_search_index", batch_size=2, verbosity=0)
        indexed = set(FeatureSearchIndex.objects.values_list("uniquename", flat=True))
        self.assertIn("GENE_A", indexed)
        self.assertIn("GENE_B", indexed)
        self.assertIn("GENE_C", indexed)
        self.assertIn("MRNA_A", indexed)
        self.assertNotIn("CHR1", indexed)
        self.assertNotIn("SNV_1", indexed)
