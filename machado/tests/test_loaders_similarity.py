# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Tests similarity data loader."""

from datetime import datetime

from Bio.Alphabet import generic_protein
from Bio.SearchIO._model import QueryResult, Hit, HSP, HSPFragment
from django.core.management import call_command
from django.test import TestCase

from machado.loaders.exceptions import ImportingError
from machado.loaders.similarity import SimilarityLoader
from machado.models import Analysis, Analysisfeature
from machado.models import Cv, Cvterm, Db, Dbxref, Organism, Pub
from machado.models import Feature, Featureloc, FeatureCvterm
from machado.models import FeatureRelationship


class SimilarityTest(TestCase):
    """Tests Loaders - SimilarityLoader."""

    def test_store_bio_searchio_blast_record(self):
        """Run Tests - __init__ and store_searchio_blast_record."""
        null_db, created = Db.objects.get_or_create(name="null")
        null_cv, created = Cv.objects.get_or_create(name="null")
        null_dbxref, created = Dbxref.objects.get_or_create(
            accession="null", db=null_db
        )
        null_cvterm, created = Cvterm.objects.get_or_create(
            name="null",
            cv=null_cv,
            dbxref=null_dbxref,
            is_obsolete=0,
            is_relationshiptype=0,
        )
        null_pub, created = Pub.objects.get_or_create(
            uniquename="null", type=null_cvterm, is_obsolete=False
        )

        test_organism = Organism.objects.create(genus="Mus", species="musculus")
        test_organism2 = Organism.objects.create(
            abbreviation="multispecies",
            genus="multispecies",
            species="multispecies",
            common_name="multispecies",
        )
        # creating test SO term
        test_db = Db.objects.create(name="SO")
        test_cv = Cv.objects.create(name="sequence")
        test_db2 = Db.objects.create(name="RO")
        test_cv2 = Cv.objects.create(name="relationship")
        test_dbxref = Dbxref.objects.create(accession="123456", db=test_db)
        test_dbxref2 = Dbxref.objects.create(accession="7890", db=test_db)
        test_aa_term = Cvterm.objects.create(
            name="polypeptide",
            cv=test_cv,
            dbxref=test_dbxref,
            is_obsolete=0,
            is_relationshiptype=0,
        )
        test_aa_term2 = Cvterm.objects.create(
            name="protein_match",
            cv=test_cv,
            dbxref=test_dbxref2,
            is_obsolete=0,
            is_relationshiptype=0,
        )
        test_dbxref3 = Dbxref.objects.create(accession="1234567", db=test_db)
        Cvterm.objects.create(
            name="match_part",
            cv=test_cv,
            dbxref=test_dbxref3,
            is_obsolete=0,
            is_relationshiptype=0,
        )
        test_dbxref4 = Dbxref.objects.create(accession="12345678", db=test_db2)
        Cvterm.objects.create(
            name="contained in",
            cv=test_cv2,
            dbxref=test_dbxref4,
            is_obsolete=0,
            is_relationshiptype=1,
        )
        test_dbxref5 = Dbxref.objects.create(accession="12345679", db=test_db2)
        Cvterm.objects.create(
            name="in similarity relationship with",
            cv=test_cv2,
            dbxref=test_dbxref5,
            is_obsolete=0,
            is_relationshiptype=1,
        )
        test_dbxref6 = Dbxref.objects.create(accession="22345679", db=test_db2)
        cvterm_translation = Cvterm.objects.create(
            name="translation_of",
            cv=test_cv,
            dbxref=test_dbxref6,
            is_obsolete=0,
            is_relationshiptype=1,
        )
        test_dbxref7 = Dbxref.objects.create(accession="223456", db=test_db)
        test_mrna_term = Cvterm.objects.create(
            name="mRNA",
            cv=test_cv,
            dbxref=test_dbxref7,
            is_obsolete=0,
            is_relationshiptype=0,
        )

        test_db_pfam = Db.objects.create(name="PFAM")
        test_cv_pfam = Cv.objects.create(name="PFAM")
        test_dbxref_pfam_term = Dbxref.objects.create(accession="123", db=test_db_pfam)
        test_cvterm_pfam_term = Cvterm.objects.create(
            name="kinase",
            cv=test_cv_pfam,
            dbxref=test_dbxref_pfam_term,
            is_obsolete=0,
            is_relationshiptype=0,
        )

        # creating test features
        feature_db = Db.objects.create(name="FASTA_SOURCE")
        feature_dbxref1 = Dbxref.objects.create(db=feature_db, accession="feat1")
        feature_dbxref2 = Dbxref.objects.create(db=feature_db, accession="feat2")
        feature_dbxref3 = Dbxref.objects.create(db=feature_db, accession="feat3")
        feature_dbxref4 = Dbxref.objects.create(db=feature_db, accession="feat4")
        feature_dbxref5 = Dbxref.objects.create(db=feature_db, accession="feat5")
        feature_dbxref1m = Dbxref.objects.create(db=feature_db, accession="feat1m")
        feature_dbxref2m = Dbxref.objects.create(db=feature_db, accession="feat2m")
        feature_dbxref3m = Dbxref.objects.create(db=feature_db, accession="feat3m")
        feature_dbxref4m = Dbxref.objects.create(db=feature_db, accession="feat4m")
        feature_dbxref5m = Dbxref.objects.create(db=feature_db, accession="feat5m")
        f1 = Feature.objects.create(
            organism=test_organism,
            uniquename="feat1",
            is_analysis=False,
            type_id=test_aa_term.cvterm_id,
            is_obsolete=False,
            dbxref=feature_dbxref1,
            timeaccessioned=datetime.now(),
            timelastmodified=datetime.now(),
        )
        f2 = Feature.objects.create(
            organism=test_organism2,
            uniquename="feat2",
            is_analysis=False,
            type_id=test_aa_term2.cvterm_id,
            is_obsolete=False,
            dbxref=feature_dbxref2,
            timeaccessioned=datetime.now(),
            timelastmodified=datetime.now(),
        )
        f3 = Feature.objects.create(
            organism=test_organism2,
            uniquename="feat3",
            is_analysis=False,
            type_id=test_aa_term2.cvterm_id,
            is_obsolete=False,
            dbxref=feature_dbxref3,
            timeaccessioned=datetime.now(),
            timelastmodified=datetime.now(),
        )
        f4 = Feature.objects.create(
            organism=test_organism,
            uniquename="feat4",
            is_analysis=False,
            type_id=test_aa_term.cvterm_id,
            is_obsolete=False,
            dbxref=feature_dbxref4,
            timeaccessioned=datetime.now(),
            timelastmodified=datetime.now(),
        )
        f5 = Feature.objects.create(
            organism=test_organism2,
            uniquename="feat5",
            is_analysis=False,
            type_id=test_aa_term2.cvterm_id,
            is_obsolete=False,
            dbxref=feature_dbxref5,
            timeaccessioned=datetime.now(),
            timelastmodified=datetime.now(),
        )
        f1m = Feature.objects.create(
            organism=test_organism,
            uniquename="feat1m",
            is_analysis=False,
            type=test_mrna_term,
            is_obsolete=False,
            dbxref=feature_dbxref1m,
            timeaccessioned=datetime.now(),
            timelastmodified=datetime.now(),
        )
        f2m = Feature.objects.create(
            organism=test_organism2,
            uniquename="feat2m",
            is_analysis=False,
            type=test_mrna_term,
            is_obsolete=False,
            dbxref=feature_dbxref2m,
            timeaccessioned=datetime.now(),
            timelastmodified=datetime.now(),
        )
        f3m = Feature.objects.create(
            organism=test_organism2,
            uniquename="feat3m",
            is_analysis=False,
            type=test_mrna_term,
            is_obsolete=False,
            dbxref=feature_dbxref3m,
            timeaccessioned=datetime.now(),
            timelastmodified=datetime.now(),
        )
        f4m = Feature.objects.create(
            organism=test_organism,
            uniquename="feat4m",
            is_analysis=False,
            type=test_mrna_term,
            is_obsolete=False,
            dbxref=feature_dbxref4m,
            timeaccessioned=datetime.now(),
            timelastmodified=datetime.now(),
        )
        f5m = Feature.objects.create(
            organism=test_organism2,
            uniquename="feat5m",
            is_analysis=False,
            type=test_mrna_term,
            is_obsolete=False,
            dbxref=feature_dbxref5m,
            timeaccessioned=datetime.now(),
            timelastmodified=datetime.now(),
        )
        FeatureRelationship.objects.create(
            subject=f1m, object=f1, type=cvterm_translation, rank=0
        )
        FeatureRelationship.objects.create(
            subject=f2m, object=f2, type=cvterm_translation, rank=0
        )
        FeatureRelationship.objects.create(
            subject=f3m, object=f3, type=cvterm_translation, rank=0
        )
        FeatureRelationship.objects.create(
            subject=f4m, object=f4, type=cvterm_translation, rank=0
        )
        FeatureRelationship.objects.create(
            subject=f5m, object=f5, type=cvterm_translation, rank=0
        )
        FeatureCvterm.objects.create(
            feature=f3, cvterm=test_cvterm_pfam_term, pub=null_pub, is_not=False, rank=0
        )

        test_HSPFragment1 = HSPFragment("feat1", "feat2")
        setattr(test_HSPFragment1, "alphabet", generic_protein)
        setattr(test_HSPFragment1, "query_start", 110)
        setattr(test_HSPFragment1, "query_end", 1100)
        setattr(test_HSPFragment1, "aln_span", 990)
        setattr(test_HSPFragment1, "hit_start", 100)
        setattr(test_HSPFragment1, "hit_end", 1000)

        test_HSP1 = HSP([test_HSPFragment1])
        setattr(test_HSP1, "query_id", "feat1")
        setattr(test_HSP1, "hit_id", "feat2")
        setattr(test_HSP1, "bitscore", 1234.0)
        setattr(test_HSP1, "bitscore_raw", 1234)
        setattr(test_HSP1, "evalue", 0.0)
        setattr(test_HSP1, "ident_num", 82)

        test_HIT1 = Hit([test_HSP1])
        setattr(test_HIT1, "accession", "5050")
        setattr(test_HIT1, "seq_len", 2000)

        test_HSPFragment2 = HSPFragment("feat1", "feat3")
        setattr(test_HSPFragment2, "alphabet", generic_protein)
        setattr(test_HSPFragment2, "query_start", 210)
        setattr(test_HSPFragment2, "query_end", 2100)
        setattr(test_HSPFragment2, "aln_span", 1890)
        setattr(test_HSPFragment2, "hit_start", 200)
        setattr(test_HSPFragment2, "hit_end", 2000)

        test_HSP2 = HSP([test_HSPFragment2])
        setattr(test_HSP2, "query_id", "feat1")
        setattr(test_HSP2, "hit_id", "feat3")
        setattr(test_HSP2, "bitscore", 234.0)
        setattr(test_HSP2, "bitscore_raw", 234)
        setattr(test_HSP2, "evalue", 0.0)
        setattr(test_HSP2, "ident_num", 72)

        test_HIT2 = Hit([test_HSP2])
        setattr(test_HIT2, "accession", "500")
        setattr(test_HIT2, "seq_len", 4000)

        test_result1 = QueryResult([test_HIT1, test_HIT2], "feat1")
        setattr(test_result1, "seq_len", 3000)
        setattr(test_result1, "blast_id", "feat1")

        # test retrieve_query_from_hsp and retrieve_subject_from_hsp
        # test hsp with no bitscore, bitscore_raw, evalue, and ident_num
        test_HSPFragment3 = HSPFragment("feat4_desc", "feat5_desc")
        setattr(test_HSPFragment3, "alphabet", generic_protein)
        setattr(test_HSPFragment3, "query_start", 210)
        setattr(test_HSPFragment3, "query_end", 2100)
        setattr(test_HSPFragment3, "aln_span", 1890)
        setattr(test_HSPFragment3, "hit_start", 200)
        setattr(test_HSPFragment3, "hit_end", 2000)

        test_HSP3 = HSP([test_HSPFragment3])
        setattr(test_HSP3, "query_id", "feat4_desc")
        setattr(test_HSP3, "query_description", "test id=feat4")
        setattr(test_HSP3, "hit_id", "feat5_desc")
        setattr(test_HSP3, "hit_description", "test id=feat5")

        test_HIT3 = Hit([test_HSP3])
        setattr(test_HIT3, "seq_len", 4000)

        test_result2 = QueryResult([test_HIT3], "feat4_desc")
        setattr(test_result2, "seq_len", 3000)
        setattr(test_result2, "blast_id", "feat4_desc")

        # test SimilarityLoader fail
        with self.assertRaises(ImportingError):
            SimilarityLoader(
                filename="similarity.file",
                algorithm="smith-waterman",
                description="command-line example",
                program="blastp",
                input_format="blast-xml",
                programversion="2.2.31+",
                so_query="polypeptide",
                so_subject="protein_match",
                org_query="Homo sapiens",
                org_subject="multispecies multispecies",
            )

        test_blast_file = SimilarityLoader(
            filename="similarity.file",
            algorithm="smith-waterman",
            description="command-line example",
            program="interproscan",
            input_format="interproscan-xml",
            programversion="5",
            so_query="polypeptide",
            so_subject="protein_match",
            org_query="Mus musculus",
            org_subject="multispecies multispecies",
        )

        test_blast_file.store_bio_searchio_query_result(test_result1)
        test_blast_file.store_bio_searchio_query_result(test_result2)

        test_analysis = Analysis.objects.get(sourcename="similarity.file")
        self.assertEqual("interproscan", test_analysis.program)

        test_featureloc = Featureloc.objects.get(srcfeature=f3)

        test_analysisfeature = Analysisfeature.objects.get(
            analysis=test_analysis, feature_id=test_featureloc.feature_id
        )
        self.assertEqual(234.0, test_analysisfeature.rawscore)
        # test remove_feature
        self.assertTrue(Analysis.objects.filter(sourcename="similarity.file").exists())
        call_command("remove_analysis", "--name=similarity.file", "--verbosity=0")
        self.assertFalse(Analysis.objects.filter(sourcename="similarity.file").exists())
