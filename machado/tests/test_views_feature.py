# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Tests feature view."""

from machado.models import Db, Dbxref, Cv, Cvterm, Organism, Pub
from machado.models import Feature, Featureloc, FeatureDbxref, FeatureCvterm
from machado.models import FeatureRelationship
from machado.views import feature
from django.test import TestCase
from datetime import datetime, timezone


class FeatureTest(TestCase):
    """Tests Feature View."""

    def setUp(self):
        """Setup."""
        null_db = Db.objects.create(name='null')
        null_cv = Cv.objects.create(name='null')
        null_dbxref = Dbxref.objects.create(
            accession='null', db=null_db)
        null_cvterm = Cvterm.objects.create(
            name='null', cv=null_cv, dbxref=null_dbxref,
            is_obsolete=0, is_relationshiptype=0)
        null_pub = Pub.objects.create(
            uniquename='null', type=null_cvterm, is_obsolete=False)

        ro_db = Db.objects.create(name='RO')
        ro_cv = Cv.objects.create(name='relationship')
        similarity_dbxref = Dbxref.objects.create(
            accession='in similarity relationship with', db=ro_db)
        similarity_cvterm = Cvterm.objects.create(
            name='in similarity relationship with', cv=ro_cv,
            dbxref=similarity_dbxref, is_obsolete=0, is_relationshiptype=0)

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
            accession='polypeptide_match', db=so_db)
        polypeptide_cvterm = Cvterm.objects.create(
            name='polypeptide', cv=so_cv, dbxref=polypeptide_dbxref,
            is_obsolete=0, is_relationshiptype=0)
        protein_match_dbxref = Dbxref.objects.create(
            accession='protein_match', db=so_db)
        protein_match_cvterm = Cvterm.objects.create(
            name='protein_match', cv=so_cv, dbxref=protein_match_dbxref,
            is_obsolete=0, is_relationshiptype=0)

        organism1 = Organism.objects.create(
            genus='Mus', species='musculus')
        multispecies_organism = Organism.objects.create(
            genus='multispecies', species='multispecies')

        chromosome_chr1 = Feature.objects.create(
            organism=organism1, uniquename='chr1', is_analysis=False,
            type=chromosome_cvterm, is_obsolete=False,
            timeaccessioned=datetime.now(timezone.utc),
            timelastmodified=datetime.now(timezone.utc))
        mRNA_feat1 = Feature.objects.create(
            organism=organism1, uniquename='feat1', is_analysis=False,
            type=mRNA_cvterm, is_obsolete=False,
            timeaccessioned=datetime.now(timezone.utc),
            timelastmodified=datetime.now(timezone.utc))
        polypeptide_feat1 = Feature.objects.create(
            organism=organism1, uniquename='feat1', is_analysis=False,
            type=polypeptide_cvterm, is_obsolete=False,
            timeaccessioned=datetime.now(timezone.utc),
            timelastmodified=datetime.now(timezone.utc))

        protein_match_PF1_db = Db.objects.create(name='PFAM')
        protein_match_PF1_dbxref = Dbxref.objects.create(
            accession='0001', db=protein_match_PF1_db)

        protein_match_PF1 = Feature.objects.create(
            organism=multispecies_organism, uniquename='PF0001',
            name='PF0001 PF0001', dbxref=protein_match_PF1_dbxref,
            type=protein_match_cvterm,
            is_analysis=False, is_obsolete=False,
            timeaccessioned=datetime.now(timezone.utc),
            timelastmodified=datetime.now(timezone.utc))

        Featureloc.objects.create(
            feature=mRNA_feat1, srcfeature=chromosome_chr1, strand=1,
            fmin=1, is_fmin_partial=False, fmax=1000, is_fmax_partial=False,
            locgroup=0, rank=0)

        mRNA_feat1_db = Db.objects.create(name='GI')
        mRNA_feat1_dbxref = Dbxref.objects.create(
            accession='12345', db=mRNA_feat1_db)
        FeatureDbxref.objects.create(
            feature=mRNA_feat1, dbxref=mRNA_feat1_dbxref, is_current=True)

        molfun_db = Db.objects.create(name='GO')
        molfun_dbxref = Dbxref.objects.create(
            accession='00001', db=molfun_db)
        go_cv = Cv.objects.create(name='molecular function')
        go_cvterm = Cvterm.objects.create(
            name='teste', definition='teste teste',
            dbxref=molfun_dbxref, cv=go_cv,
            is_obsolete=0, is_relationshiptype=0)
        FeatureCvterm.objects.create(
            feature=mRNA_feat1, cvterm=go_cvterm, pub=null_pub,
            is_not=False, rank=0)

        FeatureRelationship.objects.create(
            object=polypeptide_feat1, subject=protein_match_PF1,
            type=similarity_cvterm, rank=0)

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

    def test_retrieve_feature_dbxref(self):
        """Tests - retrieve_feature_dbxref."""
        fv = feature.FeatureView()
        f = Feature.objects.get(uniquename='feat1', type__name='mRNA')
        result = fv.retrieve_feature_dbxref(feature_id=f.feature_id)
        self.assertEqual('GI', result[0]['db'])
        self.assertEqual('12345', result[0]['dbxref'])

    def test_retrieve_feature_cvterm(self):
        """Tests - retrieve_feature_cvterm."""
        fv = feature.FeatureView()
        f = Feature.objects.get(uniquename='feat1', type__name='mRNA')
        result = fv.retrieve_feature_cvterm(feature_id=f.feature_id)
        self.assertEqual('teste', result[0]['cvterm'])
        self.assertEqual('teste teste', result[0]['cvterm_definition'])
        self.assertEqual('molecular function', result[0]['cv'])
        self.assertEqual('GO', result[0]['db'])
        self.assertEqual('00001', result[0]['dbxref'])

    def test_retrieve_feature_protein_matches(self):
        """Tests - retrieve_feature_protein_matches."""
        fv = feature.FeatureView()
        f = Feature.objects.get(uniquename='feat1', type__name='polypeptide')
        result = fv.retrieve_feature_protein_matches(feature_id=f.feature_id)
        self.assertEqual('PF0001', result[0]['subject_id'])
        self.assertEqual('PF0001 PF0001', result[0]['subject_desc'])
        self.assertEqual('PFAM', result[0]['db'])
        self.assertEqual('0001', result[0]['dbxref'])
