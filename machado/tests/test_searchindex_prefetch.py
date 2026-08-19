# Copyright 2026 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Tests for the batched prefetch step."""

from django.test import TestCase

from machado.models import Feature
from machado.searchindex import (
    IndexConfig,
    build_entries,
    detect_overlapping,
    load_valid_programs,
    prefetch_chunk,
)
from machado.tests.searchindex_fixture import build_search_index_fixture

MAX_QUERIES_PER_CHUNK = 18


class PrefetchChunkTest(TestCase):
    """prefetch_chunk gathers all related data in a bounded query count."""

    def setUp(self):
        """Build the shared fixture corpus."""
        self.features = build_search_index_fixture()
        self.config = IndexConfig(
            valid_types=["gene", "mRNA", "polypeptide"],
            overlapping_features=["SNV", "QTL", "copy_number_variation"],
            valid_programs=load_valid_programs(),
            has_overlapping=detect_overlapping(["SNV", "QTL", "copy_number_variation"]),
        )

    def _chunk(self):
        """Return the indexable features as a list."""
        return list(
            Feature.objects.filter(
                type__name__in=self.config.valid_types,
                type__cv__name="sequence",
                is_obsolete=False,
            )
            .select_related("organism", "type")
            .order_by("feature_id")
        )

    def test_gathers_related_data_for_gene_a(self):
        """Every keyword source is populated for the fully-loaded feature."""
        chunk = self._chunk()
        ids = [f.feature_id for f in chunk]
        ctx = prefetch_chunk(ids, self.config)
        gene_a = self.features["gene_a"].feature_id

        self.assertEqual(ctx.dbxref_accessions[gene_a], ["ACC_A"])
        self.assertIn(("GO", "0055085", "transmembrane transport"), ctx.cvterms[gene_a])
        self.assertIn(("PMATCH_A", "PfamHit"), ctx.protein_matches[gene_a])
        self.assertEqual(ctx.props[gene_a]["display"], ["alpha kinase"])
        self.assertEqual(ctx.props[gene_a]["orthologous group"], ["OG_1"])
        self.assertIn("10.1234/parity", ctx.dois[gene_a])
        self.assertTrue(any("catalytic activity" in a for a in ctx.annotations[gene_a]))
        self.assertTrue(ctx.samples[gene_a])
        self.assertIn("blast", ctx.analysis_programs[gene_a])
        self.assertIn(("SNV_1", "rs123"), ctx.overlaps[gene_a])

    def test_query_count_is_bounded(self):
        """Prefetching a chunk costs a fixed, small number of queries."""
        chunk = self._chunk()
        ids = [f.feature_id for f in chunk]
        with self.assertNumQueries(MAX_QUERIES_PER_CHUNK):
            prefetch_chunk(ids, self.config)

    def test_build_entries_issues_no_queries(self):
        """Assembling entries from a context touches the database zero times."""
        chunk = self._chunk()
        ctx = prefetch_chunk([f.feature_id for f in chunk], self.config)
        with self.assertNumQueries(0):
            entries = build_entries(chunk, ctx, self.config)
        self.assertEqual(len(entries), len(chunk))

    def test_empty_chunk_issues_no_queries(self):
        """An empty chunk short-circuits."""
        with self.assertNumQueries(0):
            ctx = prefetch_chunk([], self.config)
        self.assertEqual(ctx.props, {})
