# Copyright 2026 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""The feature page and the search index must resolve features identically.

This replaces the two hand-maintained "KEEP IN LOCKSTEP" comment blocks that
used to guard the duplicated copies of this logic in machado/decorators.py and
machado/searchindex.py. Both now go through machado.display; this test is what
proves it, and it is the reason those warnings could be deleted rather than
reworded.
"""

from django.test import TestCase, override_settings

from machado.display import resolve_display
from machado.models import Feature
from machado.searchindex import IndexConfig, prefetch_chunk
from machado.tests.searchindex_fixture import build_search_index_fixture


@override_settings(MACHADO_VALID_TYPES=["gene", "mRNA", "polypeptide"])
class PageIndexParityTest(TestCase):
    """Every feature resolves the same way through both paths."""

    def setUp(self):
        """Build the shared fixture corpus and prefetch it as one chunk."""
        self.features = build_search_index_fixture()
        self.config = IndexConfig.from_settings()
        self.ids = [f.feature_id for f in Feature.objects.all()]
        self.ctx = prefetch_chunk(self.ids, self.config)

    def test_display_agrees_for_every_feature(self):
        """get_display equals the index's resolve_display, feature by feature."""
        for feature in Feature.objects.all():
            fid = feature.feature_id
            with self.subTest(uniquename=feature.uniquename):
                self.assertEqual(
                    feature.get_display(),
                    resolve_display(self.ctx.props.get(fid, {})),
                )

    def test_annotations_agree_for_every_feature(self):
        """get_annotation equals the index's annotation list, in order."""
        for feature in Feature.objects.all():
            fid = feature.feature_id
            with self.subTest(uniquename=feature.uniquename):
                self.assertEqual(
                    feature.get_annotation(),
                    list(self.ctx.annotations.get(fid, [])),
                )

    def test_dois_agree_for_every_feature(self):
        """get_doi equals the index's DOI set."""
        for feature in Feature.objects.all():
            fid = feature.feature_id
            with self.subTest(uniquename=feature.uniquename):
                self.assertEqual(feature.get_doi(), set(self.ctx.dois.get(fid, set())))

    def test_the_empty_accession_shape_renders_no_doi(self):
        """A DOI accession of '' is treated as absent on both paths."""
        gene = Feature.objects.get(uniquename="GENE_EMPTY_DOI")
        self.assertEqual(gene.get_annotation(), ["no doi here"])
        self.assertEqual(gene.get_doi(), set())

    def test_the_multi_pub_shape_orders_dois_by_link_id(self):
        """Two pubs on one annotation render in featureprop_pub_id order."""
        gene = Feature.objects.get(uniquename="GENE_MULTI_PUB")
        self.assertEqual(
            gene.get_annotation(),
            ["two sources (DOI:10.5555/bbb, 10.5555/aaa)"],
        )
