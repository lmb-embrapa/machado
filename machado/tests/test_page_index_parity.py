# Copyright 2026 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""The feature page and the search index must resolve features identically.

This replaces the two hand-maintained "KEEP IN LOCKSTEP" comment blocks that
used to guard the duplicated copies of this logic in machado/decorators.py and
machado/searchindex.py. Both paths now call the same functions in
machado.display -- FeatureMixin with a single feature_id, prefetch_chunk with
a whole chunk's worth of ids -- so there is one implementation left to drift,
not two copies to keep in sync.

Read this before trusting "the tests below pass" as proof of a specific rule.
The three test_*_agree_for_every_feature tests do NOT guard the two rulings
this module exists to pin -- the truthiness filter on a DOI accession in
fetch_annotation_data, and the featureprop_pub_id ordering of a multi-pub
annotation's DOIs -- because both rules live *inside* machado.display, called
by both paths. If either rule regressed, the mixin and the index would run
the same broken function and compute the same wrong answer, so they would
still agree. What the agree-tests actually catch is a future RE-FORK: someone
adding a second, hand-rolled query path in one file that bypasses
machado.display, which is exactly how the original two-copy drift started --
so they are not dead weight, they guard the layering itself.

The two rules are pinned by test_the_empty_accession_shape_renders_no_doi and
test_the_multi_pub_shape_orders_dois_by_link_id below, which each assert an
exact literal string rather than cross-path equality. machado/tests/
test_display.py covers the same two rules again, directly, as unit tests of
machado.display with no Feature or search index involved -- read it for the
full picture.
"""

from django.test import TestCase, override_settings

from machado.display import resolve_display
from machado.models import Feature
from machado.searchindex import IndexConfig, prefetch_chunk
from machado.tests.searchindex_fixture import build_search_index_fixture


@override_settings(MACHADO_VALID_TYPES=["gene", "mRNA", "polypeptide"])
class PageIndexParityTest(TestCase):
    """Every feature resolves the same way through both paths.

    See the module docstring for what that does and does not prove.
    """

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
        """A DOI accession of '' is treated as absent on both paths.

        This is the test that pins the rule itself (an empty accession is
        truthiness-false, not "absent from a lookup dict"), not merely
        cross-path agreement -- see the module docstring.
        """
        gene = Feature.objects.get(uniquename="GENE_EMPTY_DOI")
        self.assertEqual(gene.get_annotation(), ["no doi here"])
        self.assertEqual(gene.get_doi(), set())

    def test_the_multi_pub_shape_orders_dois_by_link_id(self):
        """Two pubs on one annotation render in featureprop_pub_id order.

        This is the test that pins the ordering rule itself (DOIs sorted by
        the FeaturepropPub link's own id, not by the linked pub's id), not
        merely cross-path agreement -- see the module docstring.
        """
        gene = Feature.objects.get(uniquename="GENE_MULTI_PUB")
        self.assertEqual(
            gene.get_annotation(),
            ["two sources (DOI:10.5555/bbb, 10.5555/aaa)"],
        )
