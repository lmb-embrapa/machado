# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Tests common view."""

from datetime import datetime, timezone

from django.test import Client, TestCase, RequestFactory, override_settings
from django.urls.exceptions import NoReverseMatch

from machado.models import Db, Dbxref, Cv, Cvterm
from machado.models import Organism, OrganismPub, Pub, PubDbxref
from machado.models import Feature
from machado.views import common


class DataSummaryTest(TestCase):
    """Tests Data Summary View."""

    def test_get(self):
        """Tests - get."""
        self.factory = RequestFactory()

        Organism.objects.create(genus="Arabidopsis", species="thaliana")

        request = self.factory.get("/data/")
        ds = common.DataSummaryView()
        try:
            response = ds.get(request)
        except NoReverseMatch:
            return

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Arabidopsis thaliana")

        so_db = Db.objects.create(name="SO")
        so_cv = Cv.objects.create(name="sequence")
        assembly_dbxref = Dbxref.objects.create(accession="assembly", db=so_db)
        assembly_cvterm = Cvterm.objects.create(
            name="assembly",
            cv=so_cv,
            dbxref=assembly_dbxref,
            is_obsolete=0,
            is_relationshiptype=0,
        )
        chromosome_dbxref = Dbxref.objects.create(accession="chromosome", db=so_db)
        chromosome_cvterm = Cvterm.objects.create(
            name="chromosome",
            cv=so_cv,
            dbxref=chromosome_dbxref,
            is_obsolete=0,
            is_relationshiptype=0,
        )
        gene_dbxref = Dbxref.objects.create(accession="gene", db=so_db)
        gene_cvterm = Cvterm.objects.create(
            name="gene",
            cv=so_cv,
            dbxref=gene_dbxref,
            is_obsolete=0,
            is_relationshiptype=0,
        )
        mRNA_dbxref = Dbxref.objects.create(accession="mRNA", db=so_db)
        mRNA_cvterm = Cvterm.objects.create(
            name="mRNA",
            cv=so_cv,
            dbxref=mRNA_dbxref,
            is_obsolete=0,
            is_relationshiptype=0,
        )
        polypeptide_dbxref = Dbxref.objects.create(accession="polypeptide", db=so_db)
        polypeptide_cvterm = Cvterm.objects.create(
            name="polypeptide",
            cv=so_cv,
            dbxref=polypeptide_dbxref,
            is_obsolete=0,
            is_relationshiptype=0,
        )

        self.organism1 = Organism.objects.create(genus="Mus", species="musculus")
        self.organism2 = Organism.objects.create(genus="Homo", species="sapiens")

        Feature.objects.create(
            organism=self.organism1,
            uniquename="chr1",
            is_analysis=False,
            type=chromosome_cvterm,
            is_obsolete=False,
            timeaccessioned=datetime.now(timezone.utc),
            timelastmodified=datetime.now(timezone.utc),
        )
        Feature.objects.create(
            organism=self.organism1,
            uniquename="chr2",
            is_analysis=False,
            type=chromosome_cvterm,
            is_obsolete=False,
            timeaccessioned=datetime.now(timezone.utc),
            timelastmodified=datetime.now(timezone.utc),
        )
        Feature.objects.create(
            organism=self.organism1,
            uniquename="chr1",
            is_analysis=False,
            type=assembly_cvterm,
            is_obsolete=False,
            timeaccessioned=datetime.now(timezone.utc),
            timelastmodified=datetime.now(timezone.utc),
        )
        Feature.objects.create(
            organism=self.organism1,
            uniquename="chr2",
            is_analysis=False,
            type=assembly_cvterm,
            is_obsolete=False,
            timeaccessioned=datetime.now(timezone.utc),
            timelastmodified=datetime.now(timezone.utc),
        )
        Feature.objects.create(
            organism=self.organism1,
            uniquename="feat1",
            is_analysis=False,
            type=gene_cvterm,
            is_obsolete=False,
            timeaccessioned=datetime.now(timezone.utc),
            timelastmodified=datetime.now(timezone.utc),
        )
        Feature.objects.create(
            organism=self.organism1,
            uniquename="feat2",
            is_analysis=False,
            type=gene_cvterm,
            is_obsolete=False,
            timeaccessioned=datetime.now(timezone.utc),
            timelastmodified=datetime.now(timezone.utc),
        )
        Feature.objects.create(
            organism=self.organism1,
            uniquename="feat1",
            is_analysis=False,
            type=mRNA_cvterm,
            is_obsolete=False,
            timeaccessioned=datetime.now(timezone.utc),
            timelastmodified=datetime.now(timezone.utc),
        )
        Feature.objects.create(
            organism=self.organism1,
            uniquename="feat2",
            is_analysis=False,
            type=mRNA_cvterm,
            is_obsolete=False,
            timeaccessioned=datetime.now(timezone.utc),
            timelastmodified=datetime.now(timezone.utc),
        )
        Feature.objects.create(
            organism=self.organism1,
            uniquename="feat1",
            is_analysis=False,
            type=polypeptide_cvterm,
            is_obsolete=False,
            timeaccessioned=datetime.now(timezone.utc),
            timelastmodified=datetime.now(timezone.utc),
        )
        Feature.objects.create(
            organism=self.organism1,
            uniquename="feat2",
            is_analysis=False,
            type=polypeptide_cvterm,
            is_obsolete=False,
            timeaccessioned=datetime.now(timezone.utc),
            timelastmodified=datetime.now(timezone.utc),
        )

        Feature.objects.create(
            organism=self.organism2,
            uniquename="chr1",
            is_analysis=False,
            type=chromosome_cvterm,
            is_obsolete=False,
            timeaccessioned=datetime.now(timezone.utc),
            timelastmodified=datetime.now(timezone.utc),
        )
        Feature.objects.create(
            organism=self.organism2,
            uniquename="chr1",
            is_analysis=False,
            type=assembly_cvterm,
            is_obsolete=False,
            timeaccessioned=datetime.now(timezone.utc),
            timelastmodified=datetime.now(timezone.utc),
        )
        Feature.objects.create(
            organism=self.organism2,
            uniquename="feat1",
            is_analysis=False,
            type=gene_cvterm,
            is_obsolete=False,
            timeaccessioned=datetime.now(timezone.utc),
            timelastmodified=datetime.now(timezone.utc),
        )
        Feature.objects.create(
            organism=self.organism2,
            uniquename="feat1",
            is_analysis=False,
            type=mRNA_cvterm,
            is_obsolete=False,
            timeaccessioned=datetime.now(timezone.utc),
            timelastmodified=datetime.now(timezone.utc),
        )
        Feature.objects.create(
            organism=self.organism2,
            uniquename="feat1",
            is_analysis=False,
            type=polypeptide_cvterm,
            is_obsolete=False,
            timeaccessioned=datetime.now(timezone.utc),
            timelastmodified=datetime.now(timezone.utc),
        )
        test_pub = Pub.objects.create(
            type=chromosome_cvterm,
            uniquename="Test2018",
            title="Test Title",
            pyear="2018",
            pages="2000",
            series_name="Journal of Testing",
        )
        doi_db = Db.objects.create(name="DOI")
        doi_dbxref = Dbxref.objects.create(
            accession="10.1186/s12864-016-2535-300002", db=doi_db
        )
        PubDbxref.objects.create(pub=test_pub, dbxref=doi_dbxref, is_current=True)

        OrganismPub.objects.create(organism=self.organism1, pub=test_pub)

        request = self.factory.get("/data/")
        ds = common.DataSummaryView()
        response = ds.get(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "gene")
        self.assertContains(response, "1")
        self.assertContains(response, "mRNA")
        self.assertContains(response, "2")

    def test_get_no_settings_and_infraspecific(self):
        """Test get without MACHADO_VALID_TYPES and with infraspecific_name."""
        self.factory = RequestFactory()

        so_db = Db.objects.create(name="SO")
        so_cv = Cv.objects.create(name="sequence")
        gene_dbxref = Dbxref.objects.create(accession="gene", db=so_db)
        gene_cvterm = Cvterm.objects.create(
            name="gene",
            cv=so_cv,
            dbxref=gene_dbxref,
            is_obsolete=0,
            is_relationshiptype=0,
        )

        org = Organism.objects.create(
            genus="Zea", species="mays", infraspecific_name="subsp. mays"
        )
        Feature.objects.create(
            organism=org,
            uniquename="feat_zea",
            is_analysis=False,
            type=gene_cvterm,
            is_obsolete=False,
            timeaccessioned=datetime.now(timezone.utc),
            timelastmodified=datetime.now(timezone.utc),
        )

        from django.conf import settings

        original_valid_types = getattr(settings, "MACHADO_VALID_TYPES", None)
        if hasattr(settings, "MACHADO_VALID_TYPES"):
            delattr(settings, "MACHADO_VALID_TYPES")

        request = self.factory.get("/data/")
        ds = common.DataSummaryView()
        try:
            response = ds.get(request)
        except NoReverseMatch:
            if original_valid_types is not None:
                settings.MACHADO_VALID_TYPES = original_valid_types
            return

        if original_valid_types is not None:
            settings.MACHADO_VALID_TYPES = original_valid_types

        self.assertEqual(response.status_code, 200)

    def test_data_summary_excludes_multispecies(self):
        """Test that DataSummaryView excludes features belonging to the 'multispecies' organism."""
        self.factory = RequestFactory()

        so_db = Db.objects.create(name="SO")
        so_cv = Cv.objects.create(name="sequence")
        gene_dbxref = Dbxref.objects.create(accession="gene", db=so_db)
        gene_cvterm = Cvterm.objects.create(
            name="gene",
            cv=so_cv,
            dbxref=gene_dbxref,
            is_obsolete=0,
            is_relationshiptype=0,
        )

        org = Organism.objects.create(genus="Mus", species="musculus")
        multispecies_org = Organism.objects.create(
            genus="multispecies", species="multispecies"
        )

        Feature.objects.create(
            organism=org,
            uniquename="feat_standard",
            is_analysis=False,
            type=gene_cvterm,
            is_obsolete=False,
            timeaccessioned=datetime.now(timezone.utc),
            timelastmodified=datetime.now(timezone.utc),
        )

        Feature.objects.create(
            organism=multispecies_org,
            uniquename="feat_multi",
            is_analysis=False,
            type=gene_cvterm,
            is_obsolete=False,
            timeaccessioned=datetime.now(timezone.utc),
            timelastmodified=datetime.now(timezone.utc),
        )

        request = self.factory.get("/data/")
        ds = common.DataSummaryView()
        try:
            response = ds.get(request)
        except NoReverseMatch:
            return

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Mus musculus")
        self.assertNotContains(response, "multispecies multispecies")


class HomeViewTest(TestCase):
    """Tests Home View."""

    def test_get_home_excludes_multispecies(self):
        """Test that HomeView excludes the 'multispecies' organism and its features from statistics."""
        self.factory = RequestFactory()

        # Create standard organism and a feature
        Organism.objects.create(genus="Mus", species="musculus")
        # Create multispecies organism
        Organism.objects.create(genus="multispecies", species="multispecies")

        # Let's count them through HomeView
        request = self.factory.get("/")
        hv = common.HomeView()
        hv.request = request
        context = hv.get_context_data()

        # Since only Mus musculus should be counted (1 standard, 1 multispecies excluded)
        self.assertEqual(context["organism_count"], 1)

    @override_settings(MACHADO_SITE_TITLE="Soybean Portal")
    def test_custom_site_title_in_context(self):
        """Homeview context should contain the overridden MACHADO_SITE_TITLE when the machado_site context processor is active."""
        from machado.context_processors import machado_site

        factory = RequestFactory()
        request = factory.get("/")
        ctx = machado_site(request)
        self.assertEqual(ctx["machado_site_title"], "Soybean Portal")

    def test_default_site_title_in_context(self):
        """When no override is set, the default title should be used."""
        from machado.context_processors import machado_site

        factory = RequestFactory()
        request = factory.get("/")
        ctx = machado_site(request)
        self.assertEqual(ctx["machado_site_title"], "Machado Genomics")

    @override_settings(MACHADO_FEATURE1_TITLE="")
    def test_empty_feature_title_hides_card(self):
        """Setting a feature title to empty string should result in an empty context value (template uses {% if %} to hide it)."""
        from machado.context_processors import machado_site

        factory = RequestFactory()
        request = factory.get("/")
        ctx = machado_site(request)
        self.assertEqual(ctx["machado_feature1_title"], "")

    def test_release_notes_not_in_context_when_no_file(self):
        """machado_release_notes should be an empty list when no file exists."""
        from machado import context_processors
        from machado.context_processors import machado_site

        import tempfile
        from pathlib import Path

        context_processors._release_notes_cache = None
        with tempfile.TemporaryDirectory() as tmpdir:
            with override_settings(BASE_DIR=Path(tmpdir)):
                context_processors._release_notes_cache = None
                factory = RequestFactory()
                request = factory.get("/")
                ctx = machado_site(request)
                self.assertEqual(ctx["machado_release_notes"], [])
        context_processors._release_notes_cache = None

    def test_release_notes_in_context_when_file_exists(self):
        """machado_release_notes should contain data when file exists."""
        import json
        import tempfile
        from pathlib import Path
        from machado import context_processors
        from machado.context_processors import machado_site

        notes = [{"version": "1.0", "date": "2026-01-01", "description": "Test."}]
        context_processors._release_notes_cache = None
        with tempfile.TemporaryDirectory() as tmpdir:
            release_file = Path(tmpdir) / "release_notes.json"
            release_file.write_text(json.dumps(notes), encoding="utf-8")
            with override_settings(BASE_DIR=Path(tmpdir)):
                context_processors._release_notes_cache = None
                factory = RequestFactory()
                request = factory.get("/")
                ctx = machado_site(request)
                self.assertEqual(len(ctx["machado_release_notes"]), 1)
                self.assertEqual(ctx["machado_release_notes"][0]["version"], "1.0")
        context_processors._release_notes_cache = None

    def test_features_heading_renders_default_text(self):
        """The Features heading and subtitle render their default text."""
        client = Client()
        response = client.get("/")
        self.assertContains(response, "Key Features &amp; Capabilities")
        self.assertContains(
            response,
            "A comprehensive ecosystem designed for biological database "
            "curation and research.",
        )

    @override_settings(
        MACHADO_FEATURES_TITLE="Custom Heading",
        MACHADO_FEATURES_SUBTITLE="Custom subtitle text.",
    )
    def test_features_heading_renders_overridden_text(self):
        """The Features heading renders an overridden title and subtitle."""
        client = Client()
        response = client.get("/")
        self.assertContains(response, "Custom Heading")
        self.assertContains(response, "Custom subtitle text.")
        self.assertNotContains(response, "Key Features &amp; Capabilities")

    @override_settings(MACHADO_FEATURES_TITLE="")
    def test_features_heading_hidden_when_title_empty(self):
        """The whole Features heading is absent when its title is empty."""
        client = Client()
        response = client.get("/")
        self.assertNotContains(response, "Key Features &amp; Capabilities")
        self.assertNotContains(
            response,
            "A comprehensive ecosystem designed for biological database "
            "curation and research.",
        )

    def test_acknowledgements_absent_by_default(self):
        """The Acknowledgements section is absent when its text is empty."""
        client = Client()
        response = client.get("/")
        self.assertNotContains(response, "Acknowledgements")

    @override_settings(
        MACHADO_ACKNOWLEDGEMENTS_TEXT="Funded by the Example Grant Foundation."
    )
    def test_acknowledgements_shown_when_text_set(self):
        """The Acknowledgements section renders its title and text when set."""
        client = Client()
        response = client.get("/")
        self.assertContains(response, "Acknowledgements")
        self.assertContains(response, "Funded by the Example Grant Foundation.")

    @override_settings(
        MACHADO_ACKNOWLEDGEMENTS_TITLE="Credits",
        MACHADO_ACKNOWLEDGEMENTS_TEXT="Funded by the Example Grant Foundation.",
    )
    def test_acknowledgements_title_is_overridable(self):
        """The Acknowledgements heading uses an overridden title."""
        client = Client()
        response = client.get("/")
        self.assertContains(response, "Credits")
        self.assertNotContains(response, "Acknowledgements")
