"""Tests similarity data loader."""

from machado.models import Analysis, Analysisfeature
from machado.models import Cv, Cvterm, Db, Dbxref, Organism
from machado.models import Feature, Featureloc
from machado.loaders.similarity import SimilarityLoader
from datetime import datetime, timezone
from django.test import TestCase


class SimilarityTest(TestCase):
    """Tests Loaders - SimilarityLoader."""

    def test_store_bio_blast_record(self):
        """Tests - __init__ and store_bio_blast_record."""
        test_organism = Organism.objects.create(
            genus='Mus', species='musculus')
        # creating test SO term
        test_db = Db.objects.create(name='SO')
        test_dbxref = Dbxref.objects.create(accession='12345', db=test_db)
        test_cv = Cv.objects.create(name='sequence')
        test_gene_term = Cvterm.objects.create(
            name='gene', cv=test_cv, dbxref=test_dbxref,
            is_obsolete=0, is_relationshiptype=0)
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
            type_id=test_gene_term.cvterm_id, is_obsolete=False,
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

        # create a Bio.Blast.Record.Blast
        class BlastRecord(object):
            """mock Blast Record."""

        # create a Bio.Blast.Record.Alignment
        class BlastAlignment(object):
            """mock Alignment Record."""

        # create a Bio.Blast.Record.HSP
        class BlastHSP(object):
            """mock HSP Record."""

        test_HSP1 = BlastHSP()
        test_HSP1.identities = 98.0
        test_HSP1.score = 1234
        test_HSP1.expect = 0.0
        test_HSP1.query_start = 110
        test_HSP1.query_end = 1100
        test_HSP1.sbjct_start = 100
        test_HSP1.sbjct_end = 1000
        test_HSP2 = BlastHSP()
        test_HSP2.identities = 98.2
        test_HSP2.score = 2234
        test_HSP2.expect = 0.00000001
        test_HSP2.query_start = 200
        test_HSP2.query_end = 2000
        test_HSP2.sbjct_start = 220
        test_HSP2.sbjct_end = 2200
        test_HSP3 = BlastHSP()
        test_HSP3.identities = 93.2
        test_HSP3.score = 3234
        test_HSP3.expect = 0.00000003
        test_HSP3.query_start = 300
        test_HSP3.query_end = 3000
        test_HSP3.sbjct_start = 330
        test_HSP3.sbjct_end = 3300

        test_alignment1 = BlastAlignment()
        test_alignment1.title = 'feat2.RNA ID=feat2'
        test_alignment1.hsps = list()
        test_alignment1.hsps.append(test_HSP1)
        test_alignment2 = BlastAlignment()
        test_alignment2.title = 'feat3.RNA ID=feat3'
        test_alignment2.hsps = list()
        test_alignment1.hsps.append(test_HSP2)
        test_alignment2.hsps.append(test_HSP3)

        test_record = BlastRecord()
        test_record.query = 'feat1 ID=feat1 moltype=DNA'
        test_record.alignments = list()
        test_record.alignments.append(test_alignment1)
        test_record.alignments.append(test_alignment2)

        test_blast_file = SimilarityLoader(
                filename='similarity.file',
                algorithm='smith-waterman',
                description='command-line example',
                program='blastx',
                programversion='2.2.31+',
                so_query='gene',
                so_subject='polypeptide')

        test_blast_file.store_bio_blast_record(test_record)

        test_analysis = Analysis.objects.get(sourcename='similarity.file')
        self.assertEqual('blastx', test_analysis.program)

        test_featureloc = Featureloc.objects.get(
                srcfeature=test_feat, rank=1)

        test_analysisfeature = Analysisfeature.objects.get(
                analysis=test_analysis,
                feature_id=test_featureloc.feature_id)
        self.assertEqual(3234.0, test_analysisfeature.rawscore)
