# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Tests similarity data loader."""

from machado.models import Analysis, Analysisfeature
from machado.models import Cv, Cvterm, Db, Dbxref, Organism
from machado.models import Feature, Featureloc
from machado.loaders.similarity import SimilarityLoader
from datetime import datetime, timezone
from django.test import TestCase

import warnings
from Bio import BiopythonExperimentalWarning
with warnings.catch_warnings():
    warnings.simplefilter('ignore', BiopythonExperimentalWarning)
    from Bio.Alphabet import generic_protein
    from Bio.SearchIO._model import QueryResult, Hit, HSP, HSPFragment


class SimilarityTest(TestCase):
    """Tests Loaders - SimilarityLoader."""

    def test_store_bio_searchio_blast_record(self):
        """Run Tests - __init__ and store_searchio_blast_record."""
        test_organism = Organism.objects.create(
            genus='Mus', species='musculus')
        # creating test SO term
        test_db = Db.objects.create(name='SO')
        test_cv = Cv.objects.create(name='sequence')
        test_dbxref = Dbxref.objects.create(accession='123456', db=test_db)
        test_aa_term = Cvterm.objects.create(
            name='polypeptide', cv=test_cv, dbxref=test_dbxref,
            is_obsolete=0, is_relationshiptype=0)
        test_dbxref = Dbxref.objects.create(accession='1234567', db=test_db)
        Cvterm.objects.create(
            name='match_part', cv=test_cv, dbxref=test_dbxref,
            is_obsolete=0, is_relationshiptype=0)

        # creating test features
        Feature.objects.create(
            organism=test_organism, uniquename='feat1', is_analysis=False,
            type_id=test_aa_term.cvterm_id, is_obsolete=False,
            timeaccessioned=datetime.now(timezone.utc),
            timelastmodified=datetime.now(timezone.utc))
        Feature.objects.create(
            organism=test_organism, uniquename='feat2', is_analysis=False,
            type_id=test_aa_term.cvterm_id, is_obsolete=False,
            timeaccessioned=datetime.now(timezone.utc),
            timelastmodified=datetime.now(timezone.utc))
        test_feat = Feature.objects.create(
            organism=test_organism, uniquename='feat3', is_analysis=False,
            type_id=test_aa_term.cvterm_id, is_obsolete=False,
            timeaccessioned=datetime.now(timezone.utc),
            timelastmodified=datetime.now(timezone.utc))

        test_HSPFragment1 = HSPFragment('feat1', 'feat2')
        setattr(test_HSPFragment1, 'alphabet', generic_protein)
        setattr(test_HSPFragment1, 'query_start', 110)
        setattr(test_HSPFragment1, 'query_end', 1100)
        setattr(test_HSPFragment1, 'aln_span', 990)
        setattr(test_HSPFragment1, 'hit_start', 100)
        setattr(test_HSPFragment1, 'hit_end', 1000)

        test_HSP1 = HSP([test_HSPFragment1])
        setattr(test_HSP1, 'query_id', 'feat1')
        setattr(test_HSP1, 'hit_id', 'feat2')
        setattr(test_HSP1, 'bitscore', 1234.0)
        setattr(test_HSP1, 'bitscore_raw', 1234)
        setattr(test_HSP1, 'evalue', 0.0)
        setattr(test_HSP1, 'ident_num', 82)

        test_HIT1 = Hit([test_HSP1])
        setattr(test_HIT1, 'description', 'feat2 test')
        setattr(test_HIT1, 'accession', '5050')
        setattr(test_HIT1, 'seq_len', 2000)

        test_HSPFragment2 = HSPFragment('feat1', 'feat3')
        setattr(test_HSPFragment2, 'alphabet', generic_protein)
        setattr(test_HSPFragment2, 'query_start', 210)
        setattr(test_HSPFragment2, 'query_end', 2100)
        setattr(test_HSPFragment2, 'aln_span', 1890)
        setattr(test_HSPFragment2, 'hit_start', 200)
        setattr(test_HSPFragment2, 'hit_end', 2000)

        test_HSP2 = HSP([test_HSPFragment2])
        setattr(test_HSP2, 'query_id', 'feat1')
        setattr(test_HSP2, 'hit_id', 'feat3')
        setattr(test_HSP2, 'bitscore', 234.0)
        setattr(test_HSP2, 'bitscore_raw', 234)
        setattr(test_HSP2, 'evalue', 0.0)
        setattr(test_HSP2, 'ident_num', 72)

        test_HIT2 = Hit([test_HSP2])
        setattr(test_HIT2, 'description', 'feat3 test')
        setattr(test_HIT2, 'accession', '500')
        setattr(test_HIT2, 'seq_len', 4000)

        test_result1 = QueryResult([test_HIT1, test_HIT2], 'feat1')
        setattr(test_result1, 'description', 'feat1 test')
        setattr(test_result1, 'seq_len', 3000)
        setattr(test_result1, 'blast_id', 'feat1')

        test_blast_file = SimilarityLoader(
                filename='similarity.file',
                algorithm='smith-waterman',
                description='command-line example',
                program='blastp',
                programversion='2.2.31+',
                so_query='polypeptide',
                so_subject='polypeptide')

        test_blast_file.store_bio_searchio_query_result(test_result1)

        test_analysis = Analysis.objects.get(sourcename='similarity.file')
        self.assertEqual('blastp', test_analysis.program)

        test_featureloc = Featureloc.objects.get(
                srcfeature=test_feat)

        test_analysisfeature = Analysisfeature.objects.get(
                analysis=test_analysis,
                feature_id=test_featureloc.feature_id)
        self.assertEqual(234.0, test_analysisfeature.rawscore)
