# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Tests for machado.decorators."""

from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase
from unittest.mock import MagicMock

from machado.tests.decorators_fixture import add_annotations, build_decorator_fixture

from machado.decorators import (
    get_feature_product,
    get_feature_description,
    get_feature_note,
    get_feature_properties,
    get_feature_orthologous_group,
    get_feature_coexpression_group,
    get_feature_expression_samples,
    get_feature_cvterm,
    machado_feature_methods,
    get_pub_authors,
    machado_pub_methods,
)


class GetFeaturePropTest(TestCase):
    """Tests for feature properties decorators."""

    def test_product_found(self):
        """Test product found."""
        mock_self = MagicMock()
        mock_self.Featureprop_feature_Feature.get.return_value.value = "some product"
        result = get_feature_product(mock_self)
        self.assertEqual(result, "some product")

    def test_product_not_found(self):
        """Test product not found."""
        mock_self = MagicMock()
        mock_self.Featureprop_feature_Feature.get.side_effect = ObjectDoesNotExist
        result = get_feature_product(mock_self)
        self.assertIsNone(result)

    def test_description_found(self):
        """Test description found."""
        mock_self = MagicMock()
        mock_self.Featureprop_feature_Feature.get.return_value.value = "some desc"
        result = get_feature_description(mock_self)
        self.assertEqual(result, "some desc")

    def test_description_not_found(self):
        """Test description not found."""
        mock_self = MagicMock()
        mock_self.Featureprop_feature_Feature.get.side_effect = ObjectDoesNotExist
        result = get_feature_description(mock_self)
        self.assertIsNone(result)

    def test_note_found(self):
        """Test note found."""
        mock_self = MagicMock()
        mock_self.Featureprop_feature_Feature.get.return_value.value = "some note"
        result = get_feature_note(mock_self)
        self.assertEqual(result, "some note")

    def test_note_not_found(self):
        """Test note not found."""
        mock_self = MagicMock()
        mock_self.Featureprop_feature_Feature.get.side_effect = ObjectDoesNotExist
        result = get_feature_note(mock_self)
        self.assertIsNone(result)


class GetFeaturePropertiesTest(TestCase):
    """Tests for get_feature_properties."""

    def test_properties_found(self):
        """Test properties found."""
        mock_qs = MagicMock()
        mock_qs.exclude.return_value.order_by.return_value.values_list.return_value = [
            ("product", "val1"),
            ("note", "val2"),
        ]
        mock_self = MagicMock()
        mock_self.Featureprop_feature_Feature.filter.return_value = mock_qs

        result = get_feature_properties(mock_self)
        self.assertEqual(len(result), 2)

    def test_properties_not_found(self):
        """Test properties not found."""
        mock_self = MagicMock()
        mock_self.Featureprop_feature_Feature.filter.side_effect = ObjectDoesNotExist

        result = get_feature_properties(mock_self)
        self.assertEqual(result, [])


class GetFeatureOrthologousGroupTest(TestCase):
    """Tests for get_feature_orthologous_group."""

    def test_found(self):
        """Test found."""
        mock_self = MagicMock()
        mock_self.Featureprop_feature_Feature.get.return_value.value = "OG001"
        result = get_feature_orthologous_group(mock_self)
        self.assertEqual(result, "OG001")

    def test_not_found(self):
        """Test not found."""
        mock_self = MagicMock()
        mock_self.Featureprop_feature_Feature.get.side_effect = ObjectDoesNotExist
        result = get_feature_orthologous_group(mock_self)
        self.assertIsNone(result)


class GetFeatureCoexpressionGroupTest(TestCase):
    """Tests for get_feature_coexpression_group."""

    def test_found(self):
        """Test found."""
        mock_self = MagicMock()
        mock_self.Featureprop_feature_Feature.get.return_value.value = "CG001"
        result = get_feature_coexpression_group(mock_self)
        self.assertEqual(result, "CG001")

    def test_not_found(self):
        """Test not found."""
        mock_self = MagicMock()
        mock_self.Featureprop_feature_Feature.get.side_effect = ObjectDoesNotExist
        result = get_feature_coexpression_group(mock_self)
        self.assertIsNone(result)


class GetFeatureExpressionSamplesTest(TestCase):
    """Tests for get_feature_expression_samples."""

    def test_samples_found(self):
        """Test samples found."""
        mock_qs = MagicMock()
        mock_qs.annotate.return_value = mock_qs
        mock_qs.filter.return_value = mock_qs
        mock_qs.exclude.return_value = mock_qs
        mock_qs.values.return_value = [{"analysis__sourcename": "A", "normscore": 1.0}]

        mock_self = MagicMock()
        mock_self.Analysisfeature_feature_Feature.annotate.return_value = mock_qs

        result = get_feature_expression_samples(mock_self)
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 1)

    def test_samples_not_found(self):
        """Test samples not found."""
        mock_self = MagicMock()
        mock_self.Analysisfeature_feature_Feature.annotate.side_effect = (
            ObjectDoesNotExist
        )

        result = get_feature_expression_samples(mock_self)
        self.assertIsNone(result)


class GetFeatureCvtermTest(TestCase):
    """Tests for get_feature_cvterm."""

    def test_cvterm(self):
        """Test cvterm."""
        mock_qs = MagicMock()
        mock_qs.values.return_value = [{"name": "gene", "cv": "sequence"}]

        mock_self = MagicMock()
        mock_self.FeatureCvterm_feature_Feature.all.return_value = mock_qs

        result = get_feature_cvterm(mock_self)
        self.assertIsNotNone(result)


class MachadoFeatureMethodsTest(TestCase):
    """Tests for the machado_feature_methods decorator."""

    def test_decorator_adds_methods(self):
        """Test decorator adds methods."""

        @machado_feature_methods()
        class DummyFeature:
            """Test suite for DummyFeature."""

            pass

        self.assertTrue(hasattr(DummyFeature, "get_dbxrefs"))
        self.assertTrue(hasattr(DummyFeature, "get_display"))
        self.assertTrue(hasattr(DummyFeature, "get_product"))
        self.assertTrue(hasattr(DummyFeature, "get_description"))
        self.assertTrue(hasattr(DummyFeature, "get_note"))
        self.assertTrue(hasattr(DummyFeature, "get_annotation"))
        self.assertTrue(hasattr(DummyFeature, "get_doi"))
        self.assertTrue(hasattr(DummyFeature, "get_orthologous_group"))
        self.assertTrue(hasattr(DummyFeature, "get_coexpression_group"))
        self.assertTrue(hasattr(DummyFeature, "get_expression_samples"))
        self.assertTrue(hasattr(DummyFeature, "get_relationship"))
        self.assertTrue(hasattr(DummyFeature, "get_cvterm"))
        self.assertTrue(hasattr(DummyFeature, "get_location"))
        self.assertTrue(hasattr(DummyFeature, "get_properties"))
        self.assertTrue(hasattr(DummyFeature, "get_synonyms"))


class GetPubAuthorsTest(TestCase):
    """Tests for get_pub_authors."""

    def test_authors(self):
        """Test authors."""
        mock_qs = MagicMock()
        mock_qs.order_by.return_value.annotate.return_value.values_list.return_value = [
            "Smith John",
            "Doe Jane",
        ]

        mock_self = MagicMock()
        mock_self.Pubauthor_pub_Pub = mock_qs

        result = get_pub_authors(mock_self)
        self.assertEqual(result, "Smith John, Doe Jane")


class MachadoPubMethodsTest(TestCase):
    """Tests for the machado_pub_methods decorator."""

    def test_decorator_adds_methods(self):
        """Test decorator adds methods."""

        @machado_pub_methods()
        class DummyPub:
            """Test suite for DummyPub."""

            pass

        self.assertTrue(hasattr(DummyPub, "get_authors"))
        self.assertTrue(hasattr(DummyPub, "get_doi"))


class DecoratorRealDataTest(TestCase):
    """Characterization tests for the methods Phase 1b optimizes.

    These pin the CURRENT return values so the Phase 1b query changes can be
    shown not to alter behavior. They deliberately use real rows rather than
    mocks: a mock queryset has no query count, so it cannot detect an N+1.
    """

    def setUp(self):
        """Build the shared fixture corpus."""
        self.fx = build_decorator_fixture()

    def test_get_dbxrefs_renders_url_and_plain_forms(self):
        """A dbxref on a db with a url becomes a link; otherwise plain text."""
        result = self.fx.gene.get_dbxrefs()
        self.assertEqual(len(result), 2)
        self.assertIn(
            "<a href='https://www.example.com/12345' target='_blank'>"
            "URLDB:12345</a>",
            result,
        )
        self.assertIn("PlainDB:67890", result)

    def test_get_synonyms(self):
        """Synonym names are returned."""
        self.assertEqual(sorted(self.fx.gene.get_synonyms()), ["syn_0", "syn_1"])

    def test_get_relationship_filters_to_valid_types(self):
        """Only counterparts whose SO type is in MACHADO_VALID_TYPES appear."""
        result = self.fx.gene.get_relationship()
        names = sorted(feature.uniquename for feature in result)
        # MRNA_A (object side) and POLY_A (subject side) qualify.
        # CHR1 is a chromosome, which is not in MACHADO_VALID_TYPES.
        self.assertEqual(names, ["MRNA_A", "POLY_A"])

    def test_get_location_skips_null_srcfeature(self):
        """A Featureloc with no srcfeature produces no entry."""
        result = self.fx.gene.get_location()
        self.assertEqual(len(result), 1)
        entry = result[0]
        self.assertEqual(entry["start"], 100)
        self.assertEqual(entry["end"], 200)
        self.assertEqual(entry["ref"], "CHR1")
        self.assertIn("http://localhost/jbrowse", entry["jbrowse_url"])
        self.assertIn("Arabidopsis thaliana", entry["jbrowse_url"])
        # MACHADO_JBROWSE_OFFSET is 1200 in test settings.
        self.assertIn("CHR1:-1100..1400", entry["jbrowse_url"])
        self.assertIn("tracks=ref_seq,gene,transcripts,CDS", entry["jbrowse_url"])

    def test_get_pub_doi_returns_accession(self):
        """A pub with a DOI dbxref returns its accession."""
        self.assertEqual(self.fx.pub_with_doi.get_doi(), "10.1234/one")

    def test_get_pub_doi_returns_none_without_doi(self):
        """A pub with no DOI dbxref returns None."""
        self.assertIsNone(self.fx.pub_without_doi.get_doi())


class DecoratorDisplayAndDoiTest(TestCase):
    """Characterization tests for the display chain and annotation/DOI walk."""

    def setUp(self):
        """Build the shared fixture corpus."""
        self.fx = build_decorator_fixture()

    def test_get_display_prefers_the_display_prop(self):
        """An explicit display prop wins."""
        self.assertEqual(self.fx.gene.get_display(), "alpha kinase")

    def test_get_display_falls_back_to_product(self):
        """With no display prop, the product prop is used."""
        self.assertEqual(self.fx.mrna.get_display(), "the product")

    def test_get_display_returns_none_when_nothing_set(self):
        """A feature with none of the four props returns None."""
        self.assertIsNone(self.fx.chromosome.get_display())

    def test_get_annotation_appends_dois(self):
        """Each annotation carries its pubs' DOIs in parentheses."""
        result = self.fx.gene.get_annotation()
        self.assertEqual(len(result), 2)
        for value in result:
            self.assertIn("(DOI:", value)
            self.assertIn("10.1234/one", value)
            self.assertIn("10.1234/two", value)
        self.assertTrue(any(v.startswith("annotation 0") for v in result))

    def test_get_annotation_without_dois_is_the_bare_value(self):
        """An annotation with no DOI'd pubs is returned verbatim."""
        add_annotations(self.fx, self.fx.polypeptide, 1, with_doi=False)
        result = self.fx.polypeptide.get_annotation()
        self.assertEqual(result, ["annotation 0"])

    def test_get_doi_unions_featurepub_and_annotation_sources(self):
        """Each DOI comes from both FeaturePub pubs and annotation prop pubs."""
        result = self.fx.gene.get_doi()
        self.assertEqual(set(result), {"10.1234/one", "10.1234/two"})

    def test_get_doi_is_empty_without_any_doi(self):
        """A feature with no DOI'd pubs yields no DOIs."""
        self.assertEqual(set(self.fx.polypeptide.get_doi()), set())
