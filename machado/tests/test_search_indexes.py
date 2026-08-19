# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Tests for the rebuild_search_index management command helpers."""

from unittest.mock import MagicMock, patch

from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase

from machado.models import (
    Organism,
    Feature,
    FeatureSearchIndex,
    Cvterm,
    Cv,
    Dbxref,
    Db,
)
from machado.management.commands.rebuild_search_index import Command


class RebuildSearchIndexHelpersTest(TestCase):
    """Test suite for rebuild_search_index command helper methods."""

    def setUp(self):
        """Set up test context."""
        self.db = Db.objects.create(name="test_db")
        self.dbxref = Dbxref.objects.create(
            db=self.db, accession="test_acc", version="1"
        )
        self.cv_seq = Cv.objects.create(name="sequence")
        self.cv_prop = Cv.objects.create(name="feature_property")
        self.type_gene = Cvterm.objects.create(
            name="gene",
            cv=self.cv_seq,
            dbxref=self.dbxref,
            is_obsolete=0,
            is_relationshiptype=0,
        )
        self.org = Organism.objects.create(
            genus="Genus", species="species", common_name="Common"
        )
        self.cmd = Command()
        self.feature = Feature.objects.create(
            organism=self.org,
            uniquename="test_feature",
            name="Test Feature",
            type=self.type_gene,
            is_analysis=False,
            is_obsolete=False,
            timeaccessioned="2023-01-01T00:00:00Z",
            timelastmodified="2023-01-01T00:00:00Z",
        )

    def test_prepare_organism(self):
        """Test prepare organism."""
        self.assertEqual(self.cmd._prepare_organism(self.feature), "Genus species")
        self.feature.organism.infraspecific_name = "infra"
        self.assertEqual(
            self.cmd._prepare_organism(self.feature), "Genus species infra"
        )

    @patch("machado.management.commands.rebuild_search_index.Featureloc.objects.filter")
    @patch(
        "machado.management.commands.rebuild_search_index.Analysisfeature.objects.filter"
    )
    def test_prepare_analyses(self, mock_af_filter, mock_fl_filter):
        """Test prepare analyses."""
        valid_programs = [("blast",)]
        mock_fl_filter.return_value.filter.return_value.filter.return_value.filter.return_value.values_list.return_value = [
            1
        ]
        mock_af_filter.return_value.values_list.return_value.distinct.return_value = [
            ("blast",)
        ]

        result = self.cmd._prepare_analyses(self.feature, valid_programs)
        self.assertEqual(result, ["blast matches"])

        mock_af_filter.return_value.values_list.return_value.distinct.return_value = []
        result = self.cmd._prepare_analyses(self.feature, valid_programs)
        self.assertEqual(result, ["no blast matches"])

    @patch(
        "machado.management.commands.rebuild_search_index.FeatureDbxref.objects.filter"
    )
    @patch(
        "machado.management.commands.rebuild_search_index.FeatureCvterm.objects.filter"
    )
    @patch(
        "machado.management.commands.rebuild_search_index.FeatureRelationship.objects.filter"
    )
    def test_prepare_text(self, mock_fr_filter, mock_fc_filter, mock_fd_filter):
        """Test prepare text."""
        feature = MagicMock()
        feature.uniquename = "test_feat"
        feature.name = "Test Feat"
        feature.get_display.return_value = "Display Name"
        feature.get_annotation.return_value = ["Annotation"]
        feature.get_doi.return_value = ["10.1234/test"]
        feature.get_expression_samples.return_value = []

        mock_dbxref = MagicMock()
        mock_dbxref.dbxref.accession = "ACC123"
        mock_fd_filter.return_value = [mock_dbxref]

        mock_fc = MagicMock()
        mock_fc.cvterm.dbxref.db.name = "GO"
        mock_fc.cvterm.dbxref.accession = "000123"
        mock_fc.cvterm.name = "biological_process"
        mock_fc_filter.return_value = [mock_fc]

        mock_fr_filter.return_value = []

        text = self.cmd._prepare_text(
            feature, False, ["gene"], ["SNV", "QTL", "copy_number_variation"]
        )
        self.assertIn("Display Name", text)
        self.assertIn("ACC123", text)
        self.assertIn("GO:000123", text)
        self.assertIn("biological_process", text)
        self.assertIn("Annotation", text)
        self.assertIn("10.1234/test", text)

        # Test protein match
        mock_fr = MagicMock()
        mock_fr.subject.uniquename = "PROT1"
        mock_fr.subject.name = "Protein 1"
        mock_fr_filter.return_value = [mock_fr]
        text = self.cmd._prepare_text(
            feature, False, ["gene"], ["SNV", "QTL", "copy_number_variation"]
        )
        self.assertIn("PROT1", text)
        self.assertIn("Protein 1", text)

        # Test expression samples
        feature.get_expression_samples.return_value = [
            {
                "assay_name": "assay1",
                "biomaterial_name": "bio1",
                "biomaterial_description": "bio desc",
                "treatment_name": "treat name",
            }
        ]
        text = self.cmd._prepare_text(
            feature, False, ["gene"], ["SNV", "QTL", "copy_number_variation"]
        )
        self.assertIn("assay1", text)
        self.assertIn("bio1", text)
        self.assertIn("desc", text)
        self.assertIn("treat", text)

        # Test no name
        feature.name = None
        text = self.cmd._prepare_text(
            feature, False, ["gene"], ["SNV", "QTL", "copy_number_variation"]
        )
        self.assertNotIn("None", text)

        # Test no display
        feature.get_display.return_value = None
        text = self.cmd._prepare_text(
            feature, False, ["gene"], ["SNV", "QTL", "copy_number_variation"]
        )

    def test_prepare_doi(self):
        """Test prepare doi."""
        self.feature.get_doi = MagicMock(return_value=["doi1"])
        self.assertEqual(self.cmd._prepare_doi(self.feature), ["doi1"])

    def test_prepare_biomaterial_and_treatment(self):
        """Test prepare biomaterial and treatment."""
        sample = {"biomaterial_description": "desc", "treatment_name": "treat"}
        self.feature.get_expression_samples = MagicMock(return_value=[sample, sample])
        self.assertEqual(self.cmd._prepare_biomaterial(self.feature), ["desc"])
        self.assertEqual(self.cmd._prepare_treatment(self.feature), ["treat"])

    def test_prepare_relationship(self):
        """Test prepare relationship."""
        mock_r = MagicMock()
        mock_r.feature_id = 123
        mock_r.type.name = "part_of"
        self.feature.get_relationship = MagicMock(return_value=[mock_r])
        self.assertEqual(self.cmd._prepare_relationship(self.feature), ["123 part_of"])

    @patch("machado.management.commands.rebuild_search_index.Featureprop.objects.get")
    @patch(
        "machado.management.commands.rebuild_search_index.Featureprop.objects.filter"
    )
    @patch(
        "machado.management.commands.rebuild_search_index.FeatureRelationship.objects.filter"
    )
    def test_prepare_orthologs_coexpression(
        self, mock_fr_filter, mock_fp_filter, mock_fp_get
    ):
        """Test prepare orthologs coexpression."""
        mock_fp_get.return_value.value = "OG1"
        mock_fp_filter.return_value.values_list.return_value = [1, 2]

        mock_rel = MagicMock()
        mock_fr_filter.return_value = [mock_rel]

        # have_coexp = True
        with patch(
            "machado.management.commands.rebuild_search_index.Featureprop.objects.filter"
        ) as mock_fp_filter_inner:
            mock_fp_filter_inner.return_value.exists.return_value = True
            result = self.cmd._prepare_orthologs_coexpression(self.feature)
            self.assertIn(True, result)

            # have_coexp = False
            mock_fp_filter_inner.return_value.exists.return_value = False
            result = self.cmd._prepare_orthologs_coexpression(self.feature)
            self.assertIn(False, result)

        # Test ObjectDoesNotExist
        mock_fp_get.side_effect = ObjectDoesNotExist
        self.assertEqual(self.cmd._prepare_orthologs_coexpression(self.feature), [])


class PrepareTextDeterminismTest(TestCase):
    """autocomplete_text word order must be reproducible."""

    def test_keywords_are_sorted(self):
        """_prepare_text emits keywords in sorted order."""
        cmd = Command()
        feature = MagicMock()
        feature.uniquename = "zzz_last"
        feature.name = "aaa_first"
        feature.get_display.return_value = "mmm_middle"
        feature.get_annotation.return_value = []
        feature.get_doi.return_value = []
        feature.get_expression_samples.return_value = []
        with (
            patch(
                "machado.management.commands.rebuild_search_index."
                "FeatureDbxref.objects.filter",
                return_value=[],
            ),
            patch(
                "machado.management.commands.rebuild_search_index."
                "FeatureCvterm.objects.filter",
                return_value=[],
            ),
            patch(
                "machado.management.commands.rebuild_search_index."
                "FeatureRelationship.objects.filter",
                return_value=[],
            ),
        ):
            text = cmd._prepare_text(feature, False, ["gene"], ["SNV"])
        self.assertEqual(text, "aaa_first mmm_middle zzz_last")


class SearchVectorGeneratedColumnTest(TestCase):
    """The search_vector column is maintained by PostgreSQL, not by Python."""

    def test_search_vector_populates_on_insert(self):
        """Inserting a row computes search_vector without an explicit update."""
        db = Db.objects.create(name="gc_db")
        dbxref = Dbxref.objects.create(db=db, accession="gc_acc", version="1")
        cv = Cv.objects.create(name="sequence")
        cvterm = Cvterm.objects.create(
            name="gene", cv=cv, dbxref=dbxref, is_obsolete=0, is_relationshiptype=0
        )
        org = Organism.objects.create(genus="Gen", species="spec")
        feature = Feature.objects.create(
            organism=org,
            uniquename="gc_feature",
            name="GC Feature",
            type=cvterm,
            is_analysis=False,
            is_obsolete=False,
            timeaccessioned="2023-01-01T00:00:00Z",
            timelastmodified="2023-01-01T00:00:00Z",
        )
        FeatureSearchIndex.objects.create(
            feature=feature, autocomplete_text="kinase transporter"
        )
        row = FeatureSearchIndex.objects.get(feature=feature)
        self.assertIsNotNone(row.search_vector)
        self.assertIn(
            "kinas",
            str(row.search_vector),
            "generated tsvector should contain the indexed lexeme",
        )

    def test_search_vector_tracks_autocomplete_text_updates(self):
        """Changing autocomplete_text re-computes search_vector automatically."""
        db = Db.objects.create(name="gc_db2")
        dbxref = Dbxref.objects.create(db=db, accession="gc_acc2", version="1")
        cv = Cv.objects.create(name="sequence")
        cvterm = Cvterm.objects.create(
            name="gene", cv=cv, dbxref=dbxref, is_obsolete=0, is_relationshiptype=0
        )
        org = Organism.objects.create(genus="Gen", species="spec2")
        feature = Feature.objects.create(
            organism=org,
            uniquename="gc_feature2",
            type=cvterm,
            is_analysis=False,
            is_obsolete=False,
            timeaccessioned="2023-01-01T00:00:00Z",
            timelastmodified="2023-01-01T00:00:00Z",
        )
        row = FeatureSearchIndex.objects.create(
            feature=feature, autocomplete_text="original"
        )
        row.autocomplete_text = "replaced"
        row.save(update_fields=["autocomplete_text"])
        row.refresh_from_db()
        self.assertIn("replac", str(row.search_vector))
