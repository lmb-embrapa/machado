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
from django.test import TestCase, override_settings

from machado.models import FeatureSearchIndex
from machado.tests.searchindex_fixture import (
    build_search_index_fixture,
    snapshot_index,
)

SNAPSHOT_PATH = Path(__file__).parent / "data" / "search_index_snapshot.json"


@override_settings(MACHADO_VALID_TYPES=["gene", "mRNA", "polypeptide"])
class RebuildSearchIndexParityTest(TestCase):
    """The command's output must match the recorded snapshot exactly.

    Pinned to the stock MACHADO_VALID_TYPES regardless of what a host
    project's settings define: the fixture's SNV_1 feature exists
    specifically to prove SNV is excluded, and a deployment that legitimately
    adds SNV to its own valid types (e.g. for variant data) must not flip
    that assertion.
    """

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
        # The command must run inside this test method: each method gets its
        # own isolated transaction, so the index built by
        # test_index_matches_snapshot is rolled back and does not carry over.
        # Without this call the assertions below would inspect an empty table
        # and pass for the wrong reason.
        call_command("rebuild_search_index", batch_size=2, verbosity=0)
        indexed = set(FeatureSearchIndex.objects.values_list("uniquename", flat=True))
        self.assertIn("GENE_A", indexed)
        self.assertIn("GENE_B", indexed)
        self.assertIn("GENE_C", indexed)
        self.assertIn("MRNA_A", indexed)
        self.assertNotIn("CHR1", indexed)
        self.assertNotIn("SNV_1", indexed)


class RebuildSearchIndexQueryCountTest(TestCase):
    """The command's query count must not scale with feature count."""

    def setUp(self):
        """Build the shared fixture corpus."""
        build_search_index_fixture()

    def test_query_count_is_independent_of_batch_size(self):
        """Halving the batch size must not multiply per-feature queries."""
        from django.test.utils import CaptureQueriesContext
        from django.db import connection

        with CaptureQueriesContext(connection) as big:
            call_command("rebuild_search_index", batch_size=1000, verbosity=0)
        with CaptureQueriesContext(connection) as small:
            call_command("rebuild_search_index", batch_size=2, verbosity=0)

        # Smaller batches mean more chunks, so more queries - but the growth
        # must be proportional to chunk count, never to feature count.
        self.assertLess(
            len(big.captured_queries),
            40,
            "a single-chunk rebuild should cost a bounded number of queries",
        )
        self.assertLess(len(small.captured_queries), len(big.captured_queries) * 6)
