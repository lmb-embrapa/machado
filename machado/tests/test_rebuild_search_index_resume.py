# Copyright 2026 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Resume and restart behaviour for rebuild_search_index."""

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from machado.models import FeatureSearchIndex
from machado.tests.searchindex_fixture import (
    build_search_index_fixture,
    snapshot_index,
)


class ResumeTest(TestCase):
    """--resume continues an interrupted run without losing rows."""

    def setUp(self):
        """Build the shared fixture corpus."""
        build_search_index_fixture()

    def test_resume_completes_a_partial_index(self):
        """A partial index plus --resume equals a full rebuild."""
        call_command("rebuild_search_index", verbosity=0)
        complete = snapshot_index()

        # Simulate an interruption: drop everything above the lowest id.
        keep = (
            FeatureSearchIndex.objects.order_by("feature_id")
            .values_list("feature_id", flat=True)
            .first()
        )
        FeatureSearchIndex.objects.filter(feature_id__gt=keep).delete()
        self.assertEqual(FeatureSearchIndex.objects.count(), 1)

        call_command("rebuild_search_index", resume=True, verbosity=0)
        self.assertEqual(snapshot_index(), complete)

    def test_resume_preserves_already_indexed_rows(self):
        """--resume must not clear the index."""
        call_command("rebuild_search_index", verbosity=0)
        before = FeatureSearchIndex.objects.count()
        call_command("rebuild_search_index", resume=True, verbosity=0)
        self.assertEqual(FeatureSearchIndex.objects.count(), before)

    def test_resume_on_complete_index_is_a_noop(self):
        """Resuming a finished run indexes nothing further."""
        call_command("rebuild_search_index", verbosity=0)
        expected = snapshot_index()
        call_command("rebuild_search_index", resume=True, verbosity=0)
        self.assertEqual(snapshot_index(), expected)

    def test_no_duplicate_rows_after_resume(self):
        """feature_id is the PK, so resume can never duplicate a row."""
        call_command("rebuild_search_index", verbosity=0)
        call_command("rebuild_search_index", resume=True, verbosity=0)
        ids = list(FeatureSearchIndex.objects.values_list("feature_id", flat=True))
        self.assertEqual(len(ids), len(set(ids)))

    def test_default_rebuild_clears_the_index(self):
        """Without --resume the index is cleared first."""
        call_command("rebuild_search_index", verbosity=0)
        FeatureSearchIndex.objects.filter(uniquename="GENE_A").update(organism="STALE")
        call_command("rebuild_search_index", verbosity=0)
        row = FeatureSearchIndex.objects.get(uniquename="GENE_A")
        self.assertNotEqual(row.organism, "STALE")

    def test_restart_and_resume_are_mutually_exclusive(self):
        """Passing both flags is an error."""
        with self.assertRaises(CommandError):
            call_command("rebuild_search_index", resume=True, restart=True, verbosity=0)

    def test_max_features_caps_the_run(self):
        """--max-features stops early, for benchmarking."""
        call_command("rebuild_search_index", max_features=1, verbosity=0)
        self.assertEqual(FeatureSearchIndex.objects.count(), 1)
