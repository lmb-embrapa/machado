# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Tests feature view."""

from machado.models import Db, Dbxref, Cv, Cvterm, Organism
from machado.models import Feature, Featureloc
from machado.views import feature
from django.test import TestCase
from datetime import datetime, timezone


class FeatureTest(TestCase):
    """Tests Feature View."""

    def setUp(self):
        """Setup."""
        so_db = Db.objects.create(name='SO')
        so_cv = Cv.objects.create(name='sequence')
        chromosome_dbxref = Dbxref.objects.create(
            accession='chromosome', db=so_db)
        chromosome_cvterm = Cvterm.objects.create(
            name='chromosome', cv=so_cv, dbxref=chromosome_dbxref,
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

        test_organism = Organism.objects.create(
            genus='Mus', species='musculus')

        chromosome_chr1 = Feature.objects.create(
            organism=test_organism, uniquename='chr1', is_analysis=False,
            type=chromosome_cvterm, is_obsolete=False,
            timeaccessioned=datetime.now(timezone.utc),
            timelastmodified=datetime.now(timezone.utc))
        mRNA_feat1 = Feature.objects.create(
            organism=test_organism, uniquename='feat1', is_analysis=False,
            type=mRNA_cvterm, is_obsolete=False,
            timeaccessioned=datetime.now(timezone.utc),
            timelastmodified=datetime.now(timezone.utc))

        Featureloc.objects.create(
            feature=mRNA_feat1, srcfeature=chromosome_chr1, strand=1,
            fmin=1, is_fmin_partial=False, fmax=1000, is_fmax_partial=False,
            locgroup=0, rank=0)

    def test_retrieve_feature_location(self):
        """Tests - retrieve_feature_location."""
        fv = feature.FeatureView()
        f = Feature.objects.get(uniquename='feat1', type__name='mRNA')
        result = fv.retrieve_feature_location(
            feature_id=f.feature_id, organism='Mus musculus')
        self.assertEqual(1, result[0]['start'])
        self.assertEqual(1000, result[0]['end'])
        self.assertEqual(1, result[0]['strand'])
        self.assertEqual('chr1', result[0]['ref'])
        self.assertIn('?data=data/Mus musculus&loc=chr1:-1199..2200',
                      result[0]['jbrowse_url'])
