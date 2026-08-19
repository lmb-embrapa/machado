# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Tests for machado.decorators."""

from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase
from unittest.mock import MagicMock

from machado.tests.decorators_fixture import build_decorator_fixture

from machado.decorators import (
    get_feature_product,
    get_feature_description,
    get_feature_note,
    get_feature_annotation,
    get_feature_doi,
    get_feature_display,
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


class GetFeatureAnnotationTest(TestCase):
    """Tests for get_feature_annotation."""

    def test_annotation_with_doi(self):
        """Test annotation with doi."""
        mock_fp = MagicMock()
        mock_fp.value = "Annotation text"
        mock_fppub = MagicMock()
        mock_fppub.pub.get_doi.return_value = "10.1234/test"
        mock_fp.FeaturepropPub_featureprop_Featureprop.all.return_value = [mock_fppub]

        mock_self = MagicMock()
        mock_self.Featureprop_feature_Feature.filter.return_value = [mock_fp]

        result = get_feature_annotation(mock_self)
        self.assertEqual(len(result), 1)
        self.assertIn("DOI:10.1234/test", result[0])

    def test_annotation_without_doi(self):
        """Test annotation without doi."""
        mock_fp = MagicMock()
        mock_fp.value = "Annotation text"
        mock_fp.FeaturepropPub_featureprop_Featureprop.all.return_value = []

        mock_self = MagicMock()
        mock_self.Featureprop_feature_Feature.filter.return_value = [mock_fp]

        result = get_feature_annotation(mock_self)
        self.assertEqual(result, ["Annotation text"])

    def test_annotation_not_found(self):
        """Test annotation not found."""
        mock_self = MagicMock()
        mock_self.Featureprop_feature_Feature.filter.side_effect = ObjectDoesNotExist

        result = get_feature_annotation(mock_self)
        self.assertIsNone(result)


class GetFeatureDoiTest(TestCase):
    """Tests for get_feature_doi."""

    def test_doi_from_pubs_and_annotations(self):
        """Test doi from pubs and annotations."""
        mock_featurepub = MagicMock()
        mock_featurepub.pub.get_doi.return_value = "10.1234/pub"

        mock_fp = MagicMock()
        mock_fppub = MagicMock()
        mock_fppub.pub.get_doi.return_value = "10.1234/annot"
        mock_fp.FeaturepropPub_featureprop_Featureprop.all.return_value = [mock_fppub]

        mock_self = MagicMock()
        mock_self.FeaturePub_feature_Feature.filter.return_value = [mock_featurepub]
        mock_self.Featureprop_feature_Feature.filter.return_value = [mock_fp]

        result = get_feature_doi(mock_self)
        self.assertIn("10.1234/pub", result)
        self.assertIn("10.1234/annot", result)

    def test_doi_annotation_no_doi(self):
        """Test doi annotation no doi."""
        mock_featurepub = MagicMock()
        mock_featurepub.pub.get_doi.return_value = "10.1234/pub"

        mock_fp = MagicMock()
        mock_fp.FeaturepropPub_featureprop_Featureprop.all.return_value = []

        mock_self = MagicMock()
        mock_self.FeaturePub_feature_Feature.filter.return_value = [mock_featurepub]
        mock_self.Featureprop_feature_Feature.filter.return_value = [mock_fp]

        result = get_feature_doi(mock_self)
        self.assertIn("10.1234/pub", result)
        self.assertEqual(len(result), 1)

    def test_doi_filter_raises(self):
        """Test doi filter raises."""
        mock_self = MagicMock()
        mock_self.FeaturePub_feature_Feature.filter.return_value = []
        mock_self.Featureprop_feature_Feature.filter.side_effect = ObjectDoesNotExist

        result = get_feature_doi(mock_self)
        self.assertIsNone(result)


class GetFeatureDisplayTest(TestCase):
    """Tests for get_feature_display."""

    def test_display_found(self):
        """Test display found."""
        mock_self = MagicMock()
        mock_self.Featureprop_feature_Feature.get.return_value.value = "display text"
        result = get_feature_display(mock_self)
        self.assertEqual(result, "display text")

    def test_display_fallback_product(self):
        """Test display fallback product."""
        mock_self = MagicMock()
        mock_self.Featureprop_feature_Feature.get.side_effect = ObjectDoesNotExist
        mock_self.get_product.return_value = "product text"
        result = get_feature_display(mock_self)
        self.assertEqual(result, "product text")

    def test_display_fallback_description(self):
        """Test display fallback description."""
        mock_self = MagicMock()
        mock_self.Featureprop_feature_Feature.get.side_effect = ObjectDoesNotExist
        mock_self.get_product.return_value = None
        mock_self.get_description.return_value = "desc text"
        result = get_feature_display(mock_self)
        self.assertEqual(result, "desc text")

    def test_display_fallback_note(self):
        """Test display fallback note."""
        mock_self = MagicMock()
        mock_self.Featureprop_feature_Feature.get.side_effect = ObjectDoesNotExist
        mock_self.get_product.return_value = None
        mock_self.get_description.return_value = None
        mock_self.get_note.return_value = "note text"
        result = get_feature_display(mock_self)
        self.assertEqual(result, "note text")

    def test_display_fallback_none(self):
        """Test display fallback none."""
        mock_self = MagicMock()
        mock_self.Featureprop_feature_Feature.get.side_effect = ObjectDoesNotExist
        mock_self.get_product.return_value = None
        mock_self.get_description.return_value = None
        mock_self.get_note.return_value = None
        result = get_feature_display(mock_self)
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
