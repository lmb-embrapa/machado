# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Tests common view."""

from machado.models import Db, Dbxref, Cv, Cvterm, Organism
from machado.models import Feature
from machado.views import common
from django.test import TestCase, RequestFactory
from django.urls.exceptions import NoReverseMatch
from datetime import datetime, timezone


class DataSummaryTest(TestCase):
    """Tests Feature View."""

    def test_get(self):
        """Tests - get."""
        self.factory = RequestFactory()

        Organism.objects.create(
            genus='Arabidopsis', species='thaliana')

        request = self.factory.get('/data/')
        ds = common.DataSummaryView()
        try:
            response = ds.get(request)
        except NoReverseMatch:
            return

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Arabidopsis thaliana')

        so_db = Db.objects.create(name='SO')
        so_cv = Cv.objects.create(name='sequence')
        assembly_dbxref = Dbxref.objects.create(
            accession='assembly', db=so_db)
        assembly_cvterm = Cvterm.objects.create(
            name='assembly', cv=so_cv, dbxref=assembly_dbxref,
            is_obsolete=0, is_relationshiptype=0)
        chromosome_dbxref = Dbxref.objects.create(
            accession='chromosome', db=so_db)
        chromosome_cvterm = Cvterm.objects.create(
            name='chromosome', cv=so_cv, dbxref=chromosome_dbxref,
            is_obsolete=0, is_relationshiptype=0)
        gene_dbxref = Dbxref.objects.create(
            accession='gene', db=so_db)
        gene_cvterm = Cvterm.objects.create(
            name='gene', cv=so_cv, dbxref=gene_dbxref,
            is_obsolete=0, is_relationshiptype=0)
        mRNA_dbxref = Dbxref.objects.create(
            accession='mRNA', db=so_db)
        mRNA_cvterm = Cvterm.objects.create(
            name='mRNA', cv=so_cv, dbxref=mRNA_dbxref,
            is_obsolete=0, is_relationshiptype=0)
        polypeptide_dbxref = Dbxref.objects.create(
            accession='polypeptide', db=so_db)
        polypeptide_cvterm = Cvterm.objects.create(
            name='polypeptide', cv=so_cv, dbxref=polypeptide_dbxref,
            is_obsolete=0, is_relationshiptype=0)

        self.organism1 = Organism.objects.create(
            genus='Mus', species='musculus')
        self.organism2 = Organism.objects.create(
            genus='Homo', species='sapiens')

        Feature.objects.create(
            organism=self.organism1, uniquename='chr1', is_analysis=False,
            type=chromosome_cvterm, is_obsolete=False,
            timeaccessioned=datetime.now(timezone.utc),
            timelastmodified=datetime.now(timezone.utc))
        Feature.objects.create(
            organism=self.organism1, uniquename='chr2', is_analysis=False,
            type=chromosome_cvterm, is_obsolete=False,
            timeaccessioned=datetime.now(timezone.utc),
            timelastmodified=datetime.now(timezone.utc))
        Feature.objects.create(
            organism=self.organism1, uniquename='chr1', is_analysis=False,
            type=assembly_cvterm, is_obsolete=False,
            timeaccessioned=datetime.now(timezone.utc),
            timelastmodified=datetime.now(timezone.utc))
        Feature.objects.create(
            organism=self.organism1, uniquename='chr2', is_analysis=False,
            type=assembly_cvterm, is_obsolete=False,
            timeaccessioned=datetime.now(timezone.utc),
            timelastmodified=datetime.now(timezone.utc))
        Feature.objects.create(
            organism=self.organism1, uniquename='feat1', is_analysis=False,
            type=gene_cvterm, is_obsolete=False,
            timeaccessioned=datetime.now(timezone.utc),
            timelastmodified=datetime.now(timezone.utc))
        Feature.objects.create(
            organism=self.organism1, uniquename='feat2', is_analysis=False,
            type=gene_cvterm, is_obsolete=False,
            timeaccessioned=datetime.now(timezone.utc),
            timelastmodified=datetime.now(timezone.utc))
        Feature.objects.create(
            organism=self.organism1, uniquename='feat1', is_analysis=False,
            type=mRNA_cvterm, is_obsolete=False,
            timeaccessioned=datetime.now(timezone.utc),
            timelastmodified=datetime.now(timezone.utc))
        Feature.objects.create(
            organism=self.organism1, uniquename='feat2', is_analysis=False,
            type=mRNA_cvterm, is_obsolete=False,
            timeaccessioned=datetime.now(timezone.utc),
            timelastmodified=datetime.now(timezone.utc))
        Feature.objects.create(
            organism=self.organism1, uniquename='feat1',
            is_analysis=False, type=polypeptide_cvterm, is_obsolete=False,
            timeaccessioned=datetime.now(timezone.utc),
            timelastmodified=datetime.now(timezone.utc))
        Feature.objects.create(
            organism=self.organism1, uniquename='feat2',
            is_analysis=False, type=polypeptide_cvterm, is_obsolete=False,
            timeaccessioned=datetime.now(timezone.utc),
            timelastmodified=datetime.now(timezone.utc))

        Feature.objects.create(
            organism=self.organism2, uniquename='chr1', is_analysis=False,
            type=chromosome_cvterm, is_obsolete=False,
            timeaccessioned=datetime.now(timezone.utc),
            timelastmodified=datetime.now(timezone.utc))
        Feature.objects.create(
            organism=self.organism2, uniquename='chr1', is_analysis=False,
            type=assembly_cvterm, is_obsolete=False,
            timeaccessioned=datetime.now(timezone.utc),
            timelastmodified=datetime.now(timezone.utc))
        Feature.objects.create(
            organism=self.organism2, uniquename='feat1', is_analysis=False,
            type=gene_cvterm, is_obsolete=False,
            timeaccessioned=datetime.now(timezone.utc),
            timelastmodified=datetime.now(timezone.utc))
        Feature.objects.create(
            organism=self.organism2, uniquename='feat1', is_analysis=False,
            type=mRNA_cvterm, is_obsolete=False,
            timeaccessioned=datetime.now(timezone.utc),
            timelastmodified=datetime.now(timezone.utc))
        Feature.objects.create(
            organism=self.organism2, uniquename='feat1',
            is_analysis=False, type=polypeptide_cvterm, is_obsolete=False,
            timeaccessioned=datetime.now(timezone.utc),
            timelastmodified=datetime.now(timezone.utc))

        request = self.factory.get('/data/')
        ds = common.DataSummaryView()
        response = ds.get(request)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'assembly: 1 <br />')
        self.assertContains(response, 'assembly: 2 <br />')
