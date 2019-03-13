# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Tests JBrowse API."""

from datetime import datetime, timezone
from django.urls import include, path, reverse
from machado.loaders.feature import FeatureLoader
from machado.models import Cv, Cvterm, Db, Dbxref, Feature, Organism
from rest_framework import status
from rest_framework.test import APITestCase, URLPatternsTestCase


class JBrowseTests(APITestCase, URLPatternsTestCase):
    """Ensure we access the JBrowse API endpoint."""

    urlpatterns = [
        path('api/', include('machado.api.urls')),
    ]

    def setUp(self):
        """setUp."""
        # creates cvterm display
        test_db_null = Db.objects.create(name='null')
        test_dbxref_display = Dbxref.objects.create(accession='display',
                                                    db=test_db_null)
        test_cv_feature_property = Cv.objects.create(name='feature_property')
        Cvterm.objects.create(cv=test_cv_feature_property, name='display',
                              dbxref=test_dbxref_display, is_obsolete=0,
                              is_relationshiptype=0)

        # creates exact term
        test_db_global = Db.objects.create(name='_global')
        test_dbxref = Dbxref.objects.create(accession='exact',
                                            db=test_db_global)
        test_cv = Cv.objects.create(name='synonym_type')
        Cvterm.objects.create(
            name='exact', cv=test_cv, dbxref=test_dbxref,
            is_obsolete=0, is_relationshiptype=0)

        # creates relationship
        test_db = Db.objects.create(name='RO')
        test_dbxref = Dbxref.objects.create(accession='00002', db=test_db)
        test_cv = Cv.objects.create(name='relationship')
        Cvterm.objects.create(
            name='contained in', cv=test_cv, dbxref=test_dbxref,
            is_obsolete=0, is_relationshiptype=0)

        # creates relationship terms
        test_cv = Cv.objects.create(name='sequence')
        test_dbxref = Dbxref.objects.create(accession='part_of',
                                            db=test_db_global)
        Cvterm.objects.create(
            name='part_of', cv=test_cv, dbxref=test_dbxref,
            is_obsolete=0, is_relationshiptype=0)
        test_dbxref = Dbxref.objects.create(accession='translation_of',
                                            db=test_db_global)
        Cvterm.objects.create(
            name='translation_of', cv=test_cv, dbxref=test_dbxref,
            is_obsolete=0, is_relationshiptype=0)

        # creates SO terms: assembly, gene, and exon
        test_db = Db.objects.create(name='SO')
        test_dbxref = Dbxref.objects.create(accession='00000', db=test_db)
        test_cvterm_assembly = Cvterm.objects.create(
                name='chromosome', cv=test_cv, dbxref=test_dbxref,
                is_obsolete=0, is_relationshiptype=0)
        test_dbxref = Dbxref.objects.create(accession='00001', db=test_db)
        test_cvterm_assembly = Cvterm.objects.create(
                name='assembly', cv=test_cv, dbxref=test_dbxref,
                is_obsolete=0, is_relationshiptype=0)
        test_dbxref = Dbxref.objects.create(accession='00002', db=test_db)
        Cvterm.objects.create(name='gene', cv=test_cv, dbxref=test_dbxref,
                              is_obsolete=0, is_relationshiptype=0)
        test_dbxref = Dbxref.objects.create(accession='00003', db=test_db)
        Cvterm.objects.create(name='exon', cv=test_cv, dbxref=test_dbxref,
                              is_obsolete=0, is_relationshiptype=0)
        test_dbxref = Dbxref.objects.create(accession='00004', db=test_db)
        Cvterm.objects.create(name='polypeptide', cv=test_cv,
                              dbxref=test_dbxref, is_obsolete=0,
                              is_relationshiptype=0)
        test_dbxref = Dbxref.objects.create(accession='00005', db=test_db)
        Cvterm.objects.create(name='protein_match', cv=test_cv,
                              dbxref=test_dbxref, is_obsolete=0,
                              is_relationshiptype=0)
        test_dbxref = Dbxref.objects.create(accession='00006', db=test_db)
        Cvterm.objects.create(name='mRNA', cv=test_cv,
                              dbxref=test_dbxref, is_obsolete=0,
                              is_relationshiptype=0)
        # creates an organism
        test_organism = Organism.objects.create(
            genus='Mus', species='musculus')
        # creates a srcfeature
        test_db = Db.objects.create(name='FASTA_source')
        test_dbxref = Dbxref.objects.create(
                accession='contig1', db=test_db)
        Feature.objects.create(
                    dbxref=test_dbxref, organism=test_organism, name='contig1',
                    type=test_cvterm_assembly, uniquename='contig1',
                    is_analysis=False, is_obsolete=False,
                    timeaccessioned=datetime.now(timezone.utc),
                    timelastmodified=datetime.now(timezone.utc))

        # creates features gene and exon
        class TabixFeature(object):
            """mock tabix feature."""

        test_feat1 = TabixFeature()
        test_feat1.contig = 'contig1'
        test_feat1.feature = 'gene'
        test_feat1.start = '10'
        test_feat1.end = '100'
        test_feat1.strand = '+'
        test_feat1.frame = '1'
        test_feat1.attributes = 'id=jbrowseid1;name=name1;display=gene1'

        test_feat2 = TabixFeature()
        test_feat2.contig = 'contig1'
        test_feat2.feature = 'mRNA'
        test_feat2.start = '10'
        test_feat2.end = '100'
        test_feat2.strand = '+'
        test_feat2.frame = '1'
        test_feat2.attributes = ('id=jbrowseid1m;name=name1m;' +
                                 'display=transcript1;parent=jbrowseid1')

        test_feat3 = TabixFeature()
        test_feat3.contig = 'contig1'
        test_feat3.feature = 'exon'
        test_feat3.start = '10'
        test_feat3.end = '100'
        test_feat3.strand = '-'
        test_feat3.frame = '2'
        test_feat3.attributes = ('id=jbrowseid1e;name=name1e;display=exon1;' +
                                 'parent=jbrowseid1m')

        # instantiate the loader
        test_feat_file = FeatureLoader(filename='file.name',
                                       organism='Mus musculus',
                                       source='GFF_source')
        # store the tabix feature
        test_feat_file.store_tabix_feature(test_feat1)
        test_feat_file.store_tabix_feature(test_feat2)
        test_feat_file.store_tabix_feature(test_feat3)

    def test_jbrowse_api_global(self):
        """Retrieve JBrowse data from the global API endpoint."""
        url = reverse('jbrowse_global-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()['featureDensity'], 0.02)

    def test_jbrowse_api_features(self):
        """Retrieve JBrowse data from the features API endpoint."""
        # Tests features
        base_url = reverse('jbrowse_features-list', args=['contig1'])
        params = "soType=mRNA&organism=Mus musculus"
        url = '{}?{}'.format(base_url, params)
        response = self.client.get(url, format='json')
        response_data = response.json()['features'][0]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_data['display'], 'transcript1')
        self.assertEqual(response_data['start'], 10)
        self.assertEqual(response_data['end'], 100)

        # Tests features (return refseq - no params)
        base_url = reverse('jbrowse_features-list', args=['contig1'])
        response = self.client.get(url, format='json')
        response_data = response.json()['features'][0]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_data['start'], 10)
        self.assertEqual(response_data['end'], 100)

    def test_jbrowse_api_names(self):
        """Retrieve JBrowse data from the names API endpoint."""
        # Tests names no organism
        base_url = reverse('jbrowse_names-list')
        params = "organism=Organismus nullus"
        url = '{}?{}'.format(base_url, params)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 0)

        # Tests names equals
        base_url = reverse('jbrowse_names-list')
        params = "equals=contig1&organism=Mus musculus"
        url = '{}?{}'.format(base_url, params)
        response = self.client.get(url, format='json')
        response_data = response.json()[0]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response_data['name'], 'contig1')

        # Tests names startswith
        base_url = reverse('jbrowse_names-list')
        params = "startswith=contig1&organism=Mus musculus"
        url = '{}?{}'.format(base_url, params)
        response = self.client.get(url, format='json')
        response_data = response.json()[0]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response_data['name'], 'contig1')

        # Tests names none
        base_url = reverse('jbrowse_names-list')
        params = "organism=Mus musculus"
        url = '{}?{}'.format(base_url, params)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 0)

    def test_jbrowse_api_refseqs(self):
        """Retrieve JBrowse data from the refseqs API endpoint."""
        # Tests refseqs no organism
        base_url = reverse('jbrowse_refseqs-list')
        params = "organism=Organismus nullus"
        url = '{}?{}'.format(base_url, params)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 0)

        # Tests refseqs no soType
        base_url = reverse('jbrowse_refseqs-list')
        params = "soType=ncRNA&organism=Mus musculus"
        url = '{}?{}'.format(base_url, params)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 0)

        # Tests refseqs none
        base_url = reverse('jbrowse_refseqs-list')
        params = "soType=chromosome&organism=Mus musculus"
        url = '{}?{}'.format(base_url, params)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 0)

        # Tests refseqs
        base_url = reverse('jbrowse_refseqs-list')
        params = "soType=assembly&organism=Mus musculus"
        url = '{}?{}'.format(base_url, params)
        response = self.client.get(url, format='json')
        response_data = response.json()[0]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response_data['name'], 'contig1')
