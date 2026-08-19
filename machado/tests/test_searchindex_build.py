# Copyright 2026 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Unit tests for the pure index assembler.

These use a hand-built ChunkContext and touch no database, so they need no
mocks: build_entries is a pure function.
"""

from types import SimpleNamespace

from django.test import SimpleTestCase

from machado.searchindex import ChunkContext, IndexConfig, build_text


def _feature(feature_id=1, uniquename="GENE_A", name="Alpha"):
    """Build a stand-in feature with the attributes the assembler reads."""
    return SimpleNamespace(
        feature_id=feature_id,
        uniquename=uniquename,
        name=name,
        organism=SimpleNamespace(
            genus="Arabidopsis", species="thaliana", infraspecific_name=None
        ),
        type=SimpleNamespace(name="gene"),
    )


class BuildTextTest(SimpleTestCase):
    """build_text aggregates every keyword source, sorted and de-duplicated."""

    def setUp(self):
        """Provide a default config."""
        self.config = IndexConfig(
            valid_types=["gene", "mRNA"],
            overlapping_features=["SNV"],
            valid_programs=["blast"],
            has_overlapping=False,
        )

    def test_minimal_feature_yields_uniquename_and_name(self):
        """A feature with no related data still indexes its own identifiers."""
        text = build_text(_feature(), ChunkContext.empty(), self.config)
        self.assertEqual(text, "Alpha GENE_A")

    def test_none_name_is_not_indexed(self):
        """A null feature name must not leak the string 'None'."""
        text = build_text(_feature(name=None), ChunkContext.empty(), self.config)
        self.assertEqual(text, "GENE_A")

    def test_all_sources_are_merged_and_sorted(self):
        """Every keyword source contributes, and output is sorted."""
        ctx = ChunkContext.empty()
        ctx.dbxref_accessions[1] = ["ACC_A"]
        ctx.cvterms[1] = [("GO", "0055085", "transport")]
        ctx.protein_matches[1] = [("PMATCH_A", "PfamHit")]
        ctx.props[1] = {"display": ["kinase"]}
        ctx.annotations[1] = ["catalytic activity (DOI:10.1/x)"]
        ctx.dois[1] = {"10.1/x"}
        ctx.samples[1] = [
            {
                "assay_name": "assay_alpha",
                "biomaterial_name": "bio_alpha",
                "biomaterial_description": "leaf tissue",
                "treatment_name": "drought stress",
            }
        ]
        text = build_text(_feature(), ctx, self.config)
        for expected in [
            "ACC_A",
            "GO:0055085",
            "transport",
            "PMATCH_A",
            "PfamHit",
            "kinase",
            "catalytic activity (DOI:10.1/x)",
            "10.1/x",
            "assay_alpha",
            "bio_alpha",
            "leaf",
            "tissue",
            "drought",
            "stress",
            "GENE_A",
            "Alpha",
        ]:
            self.assertIn(expected, text)
        # Keywords are atomic units for sorting purposes: annotations (like
        # the multi-word DOI-embedded one above) are never split into
        # individual words, matching the original _prepare_text() behavior
        # in rebuild_search_index.py, which also does `keywords.add(
        # annotation)` without splitting. So the correct sortedness check
        # compares against the sorted *keyword set*, not a naive re-split
        # of the joined text on spaces -- the latter would spuriously fail
        # whenever an atomic keyword itself contains a space, exactly as
        # this multi-word annotation does.
        expected_keywords = {
            "kinase",
            "ACC_A",
            "GO:0055085",
            "transport",
            "PMATCH_A",
            "PfamHit",
            "catalytic activity (DOI:10.1/x)",
            "10.1/x",
            "assay_alpha",
            "bio_alpha",
            "leaf",
            "tissue",
            "drought",
            "stress",
            "GENE_A",
            "Alpha",
        }
        self.assertEqual(
            text, " ".join(sorted(expected_keywords)), "output must be sorted"
        )

    def test_null_sample_strings_do_not_crash(self):
        """A null biomaterial_description must not raise AttributeError."""
        ctx = ChunkContext.empty()
        ctx.samples[1] = [
            {
                "assay_name": "assay_alpha",
                "biomaterial_name": None,
                "biomaterial_description": None,
                "treatment_name": None,
            }
        ]
        text = build_text(_feature(), ctx, self.config)
        self.assertIn("assay_alpha", text)
        self.assertNotIn("None", text)

    def test_overlaps_only_included_when_enabled(self):
        """Overlapping features are indexed only when has_overlapping is set."""
        ctx = ChunkContext.empty()
        ctx.overlaps[1] = [("SNV_1", "rs123")]
        off = build_text(_feature(), ctx, self.config)
        self.assertNotIn("rs123", off)

        config_on = IndexConfig(
            valid_types=["gene"],
            overlapping_features=["SNV"],
            valid_programs=["blast"],
            has_overlapping=True,
        )
        on = build_text(_feature(), ctx, config_on)
        self.assertIn("rs123", on)
        self.assertIn("SNV_1", on)


class DisplayFallbackTest(SimpleTestCase):
    """The display value follows display -> product -> description -> note."""

    def setUp(self):
        """Provide a default config."""
        self.config = IndexConfig(
            valid_types=["gene"],
            overlapping_features=[],
            valid_programs=[],
            has_overlapping=False,
        )

    def test_display_prop_wins(self):
        """An explicit display prop takes precedence."""
        from machado.searchindex import resolve_display

        props = {"display": ["D"], "product": ["P"], "description": ["X"]}
        self.assertEqual(resolve_display(props), "D")

    def test_falls_back_through_the_chain(self):
        """Each fallback applies in order when earlier props are absent."""
        from machado.searchindex import resolve_display

        self.assertEqual(resolve_display({"product": ["P"]}), "P")
        self.assertEqual(resolve_display({"description": ["X"]}), "X")
        self.assertEqual(resolve_display({"note": ["N"]}), "N")
        self.assertIsNone(resolve_display({}))
