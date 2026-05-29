# Copyright 2026 by Embrapa. All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Tests for organism permissions and visibility access restrictions."""

from datetime import datetime, timezone
import json
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

from machado.models import (
    Db,
    Dbxref,
    Cv,
    Cvterm,
    Organism,
    Feature,
    FeatureSearchIndex,
    Featureloc,
)


class OrganismPermissionsTest(TestCase):
    """Tests organism permissions logic, views, and access restrictions."""

    def setUp(self):
        """Set up test data, user, and public/private organisms."""
        self.client = Client()
        self.admin = User.objects.create_superuser(
            username="admin", password="password", email="admin@example.com"
        )
        self.anonymous_client = Client()

        # Database setups for cvterms
        self.so_db = Db.objects.create(name="SO")
        self.so_cv = Cv.objects.create(name="sequence")
        self.gene_dbxref = Dbxref.objects.create(accession="gene", db=self.so_db)
        self.gene_cvterm = Cvterm.objects.create(
            name="gene",
            cv=self.so_cv,
            dbxref=self.gene_dbxref,
            is_obsolete=0,
            is_relationshiptype=0,
        )

        # Create organisms
        self.public_org = Organism.objects.create(
            genus="Solanum", species="lycopersicum", common_name="Tomato"
        )
        self.private_org = Organism.objects.create(
            genus="Arabidopsis", species="thaliana", common_name="Thale cress"
        )

        # Explicitly make private_org private
        self.private_org.set_public(False)

        # Create features
        self.public_feature = Feature.objects.create(
            organism=self.public_org,
            uniquename="TOMATO_GENE_1",
            name="TOMATO_GENE_1",
            is_analysis=False,
            type=self.gene_cvterm,
            is_obsolete=False,
            timeaccessioned=datetime.now(timezone.utc),
            timelastmodified=datetime.now(timezone.utc),
        )
        self.private_feature = Feature.objects.create(
            organism=self.private_org,
            uniquename="ARABIDOPSIS_GENE_1",
            name="ARABIDOPSIS_GENE_1",
            is_analysis=False,
            type=self.gene_cvterm,
            is_obsolete=False,
            timeaccessioned=datetime.now(timezone.utc),
            timelastmodified=datetime.now(timezone.utc),
        )

        # Create private subfeature and locate it on self.private_feature
        self.private_subfeature = Feature.objects.create(
            organism=self.private_org,
            uniquename="ARABIDOPSIS_SUBFEATURE_1",
            name="ARABIDOPSIS_SUBFEATURE_1",
            is_analysis=False,
            type=self.gene_cvterm,
            is_obsolete=False,
            timeaccessioned=datetime.now(timezone.utc),
            timelastmodified=datetime.now(timezone.utc),
        )
        Featureloc.objects.create(
            feature=self.private_subfeature,
            srcfeature=self.private_feature,
            strand=1,
            fmin=100,
            is_fmin_partial=False,
            fmax=500,
            is_fmax_partial=False,
            locgroup=0,
            rank=0,
        )

        # Create search indexes
        FeatureSearchIndex.objects.create(
            feature=self.public_feature,
            uniquename="TOMATO_GENE_1",
            organism="Solanum lycopersicum",
            so_term="gene",
            autocomplete_text="TOMATO_GENE_1 Solanum lycopersicum gene",
        )
        FeatureSearchIndex.objects.create(
            feature=self.private_feature,
            uniquename="ARABIDOPSIS_GENE_1",
            organism="Arabidopsis thaliana",
            so_term="gene",
            autocomplete_text="ARABIDOPSIS_GENE_1 Arabidopsis thaliana gene",
        )

    def test_model_property_and_methods(self):
        """Test is_public property and set_public method on Organism."""
        self.assertTrue(self.public_org.is_public)
        self.assertFalse(self.private_org.is_public)

        # Toggle public_org to private
        self.public_org.set_public(False)
        self.assertFalse(self.public_org.is_public)

        # Toggle private_org to public
        self.private_org.set_public(True)
        self.assertTrue(self.private_org.is_public)

    def test_permissions_panel_view_auth(self):
        """Test permissions panel view requires authentication."""
        url = reverse("loader_permissions")

        # Anonymous user gets redirected
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, 302)

        # Authenticated user gets success
        self.client.force_login(self.admin)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Solanum lycopersicum")
        self.assertContains(response, "Arabidopsis thaliana")

    def test_permissions_panel_post_toggle(self):
        """Test toggling visibility via AJAX POST updates database correctly."""
        self.client.force_login(self.admin)
        url = reverse("loader_permissions")

        # Make public_org private
        response = self.client.post(
            url,
            data=json.dumps(
                {"organism_id": self.public_org.organism_id, "is_public": False}
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data["success"])
        self.assertFalse(data["is_public"])

        # Re-check db
        self.public_org.refresh_from_db()
        self.assertFalse(self.public_org.is_public)

        # Make private_org public
        response = self.client.post(
            url,
            data=json.dumps(
                {"organism_id": self.private_org.organism_id, "is_public": True}
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data["success"])
        self.assertTrue(data["is_public"])

        self.private_org.refresh_from_db()
        self.assertTrue(self.private_org.is_public)

    def test_home_and_summary_view_restrictions(self):
        """Test counts and summaries exclude private organisms for anonymous users."""
        # 1. Anonymous Client
        home_url = reverse("home")
        response = self.anonymous_client.get(home_url)
        self.assertEqual(response.status_code, 200)
        # Should count 1 organism (self.public_org, as pre-existing public 'multispecies' is excluded)
        # and 1 feature (excluding private ones)
        self.assertEqual(response.context["organism_count"], 1)
        self.assertEqual(response.context["feature_count"], 1)

        summary_url = reverse("data_numbers")
        response = self.anonymous_client.get(summary_url)
        self.assertEqual(response.status_code, 200)
        # Summary should only include Solanum lycopersicum, not Arabidopsis thaliana
        self.assertContains(response, "Solanum lycopersicum")
        self.assertNotContains(response, "Arabidopsis thaliana")

        # 2. Authenticated Client
        self.client.force_login(self.admin)
        response = self.client.get(home_url)
        self.assertEqual(response.status_code, 200)
        # Should count all 2 organisms (public + private, default 'multispecies' excluded) and 3 features
        self.assertEqual(response.context["organism_count"], 2)
        self.assertEqual(response.context["feature_count"], 3)

        response = self.client.get(summary_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Solanum lycopersicum")
        self.assertContains(response, "Arabidopsis thaliana")

    def test_search_restrictions(self):
        """Test search excludes private organisms/features for anonymous users."""
        search_url = reverse("feature_search")

        # Anonymous search
        response = self.anonymous_client.get(search_url + "?q=GENE")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "TOMATO_GENE_1")
        self.assertNotContains(response, "ARABIDOPSIS_GENE_1")

        # Authenticated search
        self.client.force_login(self.admin)
        response = self.client.get(search_url + "?q=GENE")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "TOMATO_GENE_1")
        self.assertContains(response, "ARABIDOPSIS_GENE_1")

    def test_autocomplete_restrictions(self):
        """Test autocomplete suggestions exclude private organisms for anonymous users."""
        autocomplete_url = reverse("autocomplete_html")

        # Anonymous autocomplete
        response = self.anonymous_client.get(autocomplete_url + "?q=GENE")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "TOMATO_GENE_1")
        self.assertNotContains(response, "ARABIDOPSIS_GENE_1")

        # Authenticated autocomplete
        self.client.force_login(self.admin)
        response = self.client.get(autocomplete_url + "?q=GENE")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "TOMATO_GENE_1")
        self.assertContains(response, "ARABIDOPSIS_GENE_1")

    def test_feature_detail_view_restrictions(self):
        """Test direct detail view of private feature returns 404 for anonymous users."""
        public_url = (
            reverse("feature") + f"?feature_id={self.public_feature.feature_id}"
        )
        private_url = (
            reverse("feature") + f"?feature_id={self.private_feature.feature_id}"
        )

        # Anonymous client accesses public feature
        response = self.anonymous_client.get(public_url)
        self.assertEqual(response.status_code, 200)

        # Anonymous client accesses private feature -> 404
        response = self.anonymous_client.get(private_url)
        self.assertEqual(response.status_code, 404)

        # Authenticated client accesses private feature -> 200
        self.client.force_login(self.admin)
        response = self.client.get(private_url)
        self.assertEqual(response.status_code, 200)

    def test_jbrowse_endpoints_restrictions(self):
        """Test JBrowse refseqs, names, and features exclude private data for anonymous users."""
        from django.core.cache import cache

        # ── Test refseqs ──
        refseqs_url = reverse("jbrowse_refseqs")

        # Anonymous accesses private organism refseqs -> returns empty
        response = self.anonymous_client.get(
            refseqs_url + "?organism=Arabidopsis%20thaliana"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), [])

        # Authenticated accesses private organism refseqs -> success
        cache.clear()
        self.client.force_login(self.admin)
        response = self.client.get(refseqs_url + "?organism=Arabidopsis%20thaliana")
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(json.loads(response.content), [])

        # ── Test names ──
        names_url = reverse("jbrowse_names")

        # Anonymous accesses private organism names -> returns empty
        response = self.anonymous_client.get(
            names_url + "?organism=Arabidopsis%20thaliana"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), [])

        # Authenticated accesses private organism names -> success
        cache.clear()
        response = self.client.get(names_url + "?organism=Arabidopsis%20thaliana")
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(json.loads(response.content), [])

        # ── Test features ──
        features_url = reverse(
            "jbrowse_features", kwargs={"refseq": "ARABIDOPSIS_GENE_1"}
        )

        # Anonymous accesses private features -> returns empty features object
        response = self.anonymous_client.get(
            features_url + "?organism=Arabidopsis%20thaliana"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {"features": []})

        # Authenticated accesses private features -> returns features
        cache.clear()
        response = self.client.get(features_url + "?organism=Arabidopsis%20thaliana")
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(json.loads(response.content), {"features": []})
