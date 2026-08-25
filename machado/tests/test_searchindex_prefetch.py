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
    IndexRunCache,
    build_entries,
    detect_overlapping,
    load_valid_programs,
    prefetch_chunk,
)
from machado.tests.searchindex_fixture import build_search_index_fixture

#: Queries ``prefetch_chunk`` issues for one chunk, whatever its size. This is
#: an exact expected value, not a ceiling: raising it is only ever correct
#: when a query was deliberately added, never to accommodate a count that grew
#: with the number of features in the chunk.
MAX_QUERIES_PER_CHUNK = 16


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
        # Both assertions below hold trivially on an empty chunk, and this test
        # is the only guard against reintroducing the per-feature N+1.
        self.assertGreater(len(chunk), 0, "fixture must yield indexable features")
        with self.assertNumQueries(0):
            entries = build_entries(chunk, ctx, self.config)
        self.assertEqual(len(entries), len(chunk))

    def test_overlap_candidates_are_bounded_in_sql(self):
        """The overlap query must carry its coordinate window into SQL.

        Guards a performance property no output assertion can see: with only
        ``srcfeature_id`` in the WHERE clause and the window applied in
        Python, this query returns every SNV/QTL/CNV featureloc on the whole
        chromosome (millions of rows on a resequencing project) and cannot use
        the ``featureloc (srcfeature_id, fmin, fmax)`` index.
        """
        from django.db import connection
        from django.test.utils import CaptureQueriesContext

        with CaptureQueriesContext(connection) as captured:
            prefetch_chunk([f.feature_id for f in self._chunk()], self.config)

        overlap_queries = [
            q["sql"]
            for q in captured.captured_queries
            if "featureloc" in q["sql"] and "'SNV'" in q["sql"]
        ]
        self.assertTrue(overlap_queries, "no overlap candidate query was issued")
        for sql in overlap_queries:
            self.assertIn('"fmin" <=', sql, sql)
            self.assertIn('"fmax" >=', sql, sql)

    def test_run_cache_reuses_chunk_independent_lookups(self):
        """A warm IndexRunCache skips the ortholog queries, same output."""
        from django.db import connection
        from django.test.utils import CaptureQueriesContext

        ids = [f.feature_id for f in self._chunk()]
        cache = IndexRunCache()
        cold = prefetch_chunk(ids, self.config, cache=cache)
        self.assertTrue(cache.ortholog_flags, "nothing was memoised")

        with CaptureQueriesContext(connection) as captured:
            warm = prefetch_chunk(ids, self.config, cache=cache)

        self.assertLess(len(captured.captured_queries), MAX_QUERIES_PER_CHUNK)
        self.assertEqual(warm.orthologs_coexpression, cold.orthologs_coexpression)
        self.assertEqual(
            warm.orthologs_coexpression,
            prefetch_chunk(ids, self.config).orthologs_coexpression,
            "the cache changed the facet value",
        )
        # The facet value is a single bool per feature, so there is no shared
        # mutable list left for a chunk to alias into the cache.
        for flag in warm.orthologs_coexpression.values():
            self.assertIsInstance(flag, bool)

    def test_multi_doi_pub_picks_the_lowest_pk_dbxref(self):
        """A pub with two DOI dbxrefs resolves to the lowest-pk one.

        Twin of DecoratorAnnotationQueryTest.
        test_multi_doi_pub_picks_the_lowest_pk_dbxref. Without an explicit
        ORDER BY, the setdefault below keeps whichever row the query plan
        returned first, so FeatureSearchIndex.doi could flip between rebuilds
        and disagree with what feature.html shows for the same feature.
        """
        from machado.models import Db, Dbxref, Pub, PubDbxref

        pub = Pub.objects.get(uniquename="PUB:1")
        later = Dbxref.objects.create(
            db=Db.objects.get(name="DOI"), accession="10.9999/later", version="1"
        )
        PubDbxref.objects.create(pub=pub, dbxref=later, is_current=True)

        ctx = prefetch_chunk([f.feature_id for f in self._chunk()], self.config)
        gene_a = self.features["gene_a"].feature_id
        self.assertIn("10.1234/parity", ctx.dois[gene_a])
        self.assertNotIn("10.9999/later", ctx.dois[gene_a])

    def test_empty_chunk_issues_no_queries(self):
        """An empty chunk short-circuits."""
        with self.assertNumQueries(0):
            ctx = prefetch_chunk([], self.config)
        self.assertEqual(ctx.props, {})
