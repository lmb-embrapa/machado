# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Tests coexpression data loader."""

from datetime import datetime

from django.test import TestCase

from machado.loaders.feature import FeatureLoader
from machado.models import Cv, Cvterm, Db, Dbxref, Organism
from machado.models import Feature, Featureprop
from machado.models import FeatureRelationship, FeatureRelationshipprop


class CoexpressionTest(TestCase):
    """Tests Loaders - CoexpressionLoader."""

    def test_load_coexpression_pairs(self):
        """Run tests of load_coexpression_pairs."""
        """Load 'pcc.mcl.txt' output result file from LSTrAP.
    The 'pcc.mcl.txt' file is headless and have the format as follows:
    AT2G44195.1.TAIR10	AT1G30080.1.TAIR10	0.18189286870895194
    AT2G44195.1.TAIR10	AT5G24750.1.TAIR10	0.1715779378273995
    ...
    and so on.
    The value of the third column is a Pearson correlation coefficient
    subtracted from 0.7 (PCC - 0.7). To obtain the original PCC value,
    it must be added 0.7 to every value of the third column."""
        # register multispecies organism
        test_organism = Organism.objects.create(
            abbreviation="multispecies",
            genus="multispecies",
            species="multispecies",
            common_name="multispecies",
        )
        # creating test SO term
        test_db = Db.objects.create(name="SO")
        test_cv = Cv.objects.create(name="sequence")
        # creating test RO term
        test_db2 = Db.objects.create(name="RO")
        test_cv2 = Cv.objects.create(name="relationship")

        # test_dbxref = Dbxref.objects.create(accession='123456', db=test_db)
        test_dbxref2 = Dbxref.objects.create(accession="789", db=test_db2)
        test_dbxref3 = Dbxref.objects.create(accession="135", db=test_db)
        test_dbxref4 = Dbxref.objects.create(accession="246", db=test_db2)
        test_dbxref6 = Dbxref.objects.create(accession="357", db=test_db)
        test_dbxref7 = Dbxref.objects.create(accession="468", db=test_db)
        Cvterm.objects.create(
            name="mRNA",
            cv=test_cv,
            dbxref=test_dbxref3,
            is_obsolete=0,
            is_relationshiptype=0,
        )
        # Cvterm.objects.create(
        #     name='polypeptide', cv=test_cv, dbxref=test_dbxref,
        #    is_obsolete=0, is_relationshiptype=0)
        # register features.
        cvterm_contained_in = Cvterm.objects.create(
            name="contained in",
            cv=test_cv2,
            dbxref=test_dbxref2,
            is_obsolete=0,
            is_relationshiptype=1,
        )
        term = Cvterm.objects.create(
            name="correlated with",
            cv=test_cv2,
            dbxref=test_dbxref4,
            is_obsolete=0,
            is_relationshiptype=1,
        )
        test_term = Cvterm.objects.create(
            name="polypeptide",
            cv=test_cv,
            dbxref=test_dbxref6,
            is_obsolete=0,
            is_relationshiptype=0,
        )
        Cvterm.objects.create(
            name="protein_match",
            cv=test_cv,
            dbxref=test_dbxref7,
            is_obsolete=0,
            is_relationshiptype=0,
        )
        db = Db.objects.create(name="FASTA_SOURCE")
        # creating test features
        test_featurename1 = "AT2G44195.1.TAIR10"
        dbxref1 = Dbxref.objects.create(db=db, accession=test_featurename1)
        test_feature1 = Feature.objects.create(
            organism=test_organism,
            dbxref=dbxref1,
            uniquename=test_featurename1,
            is_analysis=False,
            type_id=test_term.cvterm_id,
            is_obsolete=False,
            timeaccessioned=datetime.now(),
            timelastmodified=datetime.now(),
        )
        test_featurename2 = "AT1G30080.1.TAIR10"
        dbxref2 = Dbxref.objects.create(db=db, accession=test_featurename2)
        test_feature2 = Feature.objects.create(
            organism=test_organism,
            dbxref=dbxref2,
            uniquename=test_featurename2,
            is_analysis=False,
            type_id=test_term.cvterm_id,
            is_obsolete=False,
            timeaccessioned=datetime.now(),
            timelastmodified=datetime.now(),
        )
        test_featurename3 = "AT5G24750.1.TAIR10"
        dbxref3 = Dbxref.objects.create(db=db, accession=test_featurename3)
        test_feature3 = Feature.objects.create(
            dbxref=dbxref3,
            organism=test_organism,
            uniquename=test_featurename3,
            is_analysis=False,
            type_id=test_term.cvterm_id,
            is_obsolete=False,
            timeaccessioned=datetime.now(),
            timelastmodified=datetime.now(),
        )
        test_pair1 = [test_featurename1, test_featurename2]
        test_pair2 = [test_featurename1, test_featurename3]
        test_value1 = 0.1818928687089519
        test_value2 = 0.1715779378273995
        test_pcc_value1 = str(test_value1 + 0.7)
        test_pcc_value2 = str(test_value2 + 0.7)
        # dummy coexpression variables
        test_filename = "pcc.mcl.dummy.txt"
        source = "null"
        soterm = "polypeptide"
        test_coexpression_loader = FeatureLoader(source=source, filename=test_filename)
        test_coexpression_loader.store_feature_pairs(
            pair=test_pair1, soterm=soterm, term=term, value=test_pcc_value1
        )
        test_coexpression_loader.store_feature_pairs(
            pair=test_pair2, soterm=soterm, term=term, value=test_pcc_value2
        )
        # start checking
        self.assertTrue(
            FeatureRelationship.objects.filter(
                subject_id=test_feature1.feature_id,
                object_id=test_feature2.feature_id,
                value=test_pcc_value1,
            ).exists()
        )
        self.assertTrue(
            FeatureRelationship.objects.filter(
                subject_id=test_feature1.feature_id,
                object_id=test_feature3.feature_id,
                value=test_pcc_value2,
            ).exists()
        )
        fr1 = FeatureRelationship.objects.get(
            subject_id=test_feature1.feature_id,
            object_id=test_feature2.feature_id,
            value=test_pcc_value1,
        )
        fr2 = FeatureRelationship.objects.get(
            subject_id=test_feature1.feature_id,
            object_id=test_feature3.feature_id,
            value=test_pcc_value2,
        )
        self.assertTrue(
            FeatureRelationshipprop.objects.filter(
                feature_relationship=fr1,
                type_id=cvterm_contained_in.cvterm_id,
                value=test_filename,
            ).exists()
        )
        self.assertTrue(
            FeatureRelationshipprop.objects.filter(
                feature_relationship=fr2,
                type_id=cvterm_contained_in.cvterm_id,
                value=test_filename,
            ).exists()
        )

    def test_load_coexpression_clusters(self):
        """Run tests of load_coexpression_pairs."""
        """Load 'mcl.clusters.txt' output result file from LSTrAP.
        The 'mcl.clusters.txt' is a tab separated, headless file and have the
        format as follows (each line is a cluster):
        ath_coexpr_mcl_1:   AT3G18715.1.TAIR10 AT3G08790.1.TAIR10
        AT5G42230.1.TAIR10
        ath_coexpr_mcl_1:   AT1G27040.1.TAIR10 AT1G71692.1.TAIR10
        ath_coexpr_mcl_1:   AT5G24750.1.TAIR10
        ...
        and so on.
        The features need to be loaded previously or won't be registered."""
        # register multispecies organism
        test_organism = Organism.objects.create(
            abbreviation="multispecies",
            genus="multispecies",
            species="multispecies",
            common_name="multispecies",
        )
        # creating test SO term
        test_db = Db.objects.create(name="SO")
        test_cv = Cv.objects.create(name="sequence")
        # creating test RO term
        test_db2 = Db.objects.create(name="RO")
        test_cv2 = Cv.objects.create(name="relationship")
        test_cv3 = Cv.objects.create(name="feature_property")

        # test_dbxref = Dbxref.objects.create(accession='123456', db=test_db)
        test_dbxref2 = Dbxref.objects.create(accession="028", db=test_db)
        test_dbxref3 = Dbxref.objects.create(accession="135", db=test_db)
        test_dbxref4 = Dbxref.objects.create(accession="246", db=test_db2)
        test_dbxref5 = Dbxref.objects.create(accession="579", db=test_db2)
        test_dbxref6 = Dbxref.objects.create(accession="357", db=test_db)
        test_dbxref7 = Dbxref.objects.create(accession="468", db=test_db)
        Cvterm.objects.create(
            name="mRNA",
            cv=test_cv,
            dbxref=test_dbxref3,
            is_obsolete=0,
            is_relationshiptype=0,
        )
        # Cvterm.objects.create(
        #     name='polypeptide', cv=test_cv, dbxref=test_dbxref,
        #    is_obsolete=0, is_relationshiptype=0)
        # register features.
        Cvterm.objects.create(
            name="contained in",
            cv=test_cv2,
            dbxref=test_dbxref2,
            is_obsolete=0,
            is_relationshiptype=1,
        )
        Cvterm.objects.create(
            name="correlated with",
            cv=test_cv2,
            dbxref=test_dbxref4,
            is_obsolete=0,
            is_relationshiptype=1,
        )
        term = Cvterm.objects.create(
            name="coexpression group",
            cv=test_cv3,
            dbxref=test_dbxref5,
            is_obsolete=0,
            is_relationshiptype=0,
        )
        test_term = Cvterm.objects.create(
            name="polypeptide",
            cv=test_cv,
            dbxref=test_dbxref6,
            is_obsolete=0,
            is_relationshiptype=0,
        )
        Cvterm.objects.create(
            name="protein_match",
            cv=test_cv,
            dbxref=test_dbxref7,
            is_obsolete=0,
            is_relationshiptype=0,
        )
        db = Db.objects.create(name="FASTA_SOURCE")

        test_featurename1 = "AT3G18715.1.TAIR10"
        dbxref1 = Dbxref.objects.create(db=db, accession=test_featurename1)
        test_feature1 = Feature.objects.create(
            dbxref=dbxref1,
            organism=test_organism,
            uniquename=test_featurename1,
            is_analysis=False,
            type_id=test_term.cvterm_id,
            is_obsolete=False,
            timeaccessioned=datetime.now(),
            timelastmodified=datetime.now(),
        )
        test_featurename2 = "AT3G08790.1.TAIR10"

        dbxref2 = Dbxref.objects.create(db=db, accession=test_featurename2)
        test_feature2 = Feature.objects.create(
            dbxref=dbxref2,
            organism=test_organism,
            uniquename=test_featurename2,
            is_analysis=False,
            type_id=test_term.cvterm_id,
            is_obsolete=False,
            timeaccessioned=datetime.now(),
            timelastmodified=datetime.now(),
        )
        test_featurename3 = "AT5G42230.1.TAIR10"

        dbxref3 = Dbxref.objects.create(db=db, accession=test_featurename3)
        test_feature3 = Feature.objects.create(
            dbxref=dbxref3,
            organism=test_organism,
            uniquename=test_featurename3,
            is_analysis=False,
            type_id=test_term.cvterm_id,
            is_obsolete=False,
            timeaccessioned=datetime.now(),
            timelastmodified=datetime.now(),
        )

        test_featurename4 = "AT1G27040.1.TAIR10"
        dbxref4 = Dbxref.objects.create(db=db, accession=test_featurename4)
        test_feature4 = Feature.objects.create(
            dbxref=dbxref4,
            organism=test_organism,
            uniquename=test_featurename4,
            is_analysis=False,
            type_id=test_term.cvterm_id,
            is_obsolete=False,
            timeaccessioned=datetime.now(),
            timelastmodified=datetime.now(),
        )

        test_featurename5 = "AT1G71692.1.TAIR10"
        dbxref5 = Dbxref.objects.create(db=db, accession=test_featurename5)
        test_feature5 = Feature.objects.create(
            dbxref=dbxref5,
            organism=test_organism,
            uniquename=test_featurename5,
            is_analysis=False,
            type_id=test_term.cvterm_id,
            is_obsolete=False,
            timeaccessioned=datetime.now(),
            timelastmodified=datetime.now(),
        )

        test_featurename6 = "AT5G24750.1.TAIR10"
        dbxref6 = Dbxref.objects.create(db=db, accession=test_featurename6)
        test_feature6 = Feature.objects.create(
            dbxref=dbxref6,
            organism=test_organism,
            uniquename=test_featurename6,
            is_analysis=False,
            type_id=test_term.cvterm_id,
            is_obsolete=False,
            timeaccessioned=datetime.now(),
            timelastmodified=datetime.now(),
        )

        # clusters setup
        test_cluster1_name = "ath_coexpr_mcl_1"
        test_cluster1 = [test_featurename1, test_featurename2, test_featurename3]
        test_cluster2_name = "ath_coexpr_mcl_2"
        test_cluster2 = [test_featurename4, test_featurename5]
        test_cluster3_name = "ath_coexpr_mcl_3"
        test_cluster3 = [test_featurename6]
        test_filename = "mcl.clusters.dummy.txt"
        source = "null"
        test_coexpression_loader = FeatureLoader(source=source, filename=test_filename)
        soterm = "polypeptide"
        test_coexpression_loader.store_feature_groups(
            group=test_cluster1, soterm=soterm, term=term, value=test_cluster1_name
        )
        test_coexpression_loader.store_feature_groups(
            group=test_cluster2, soterm=soterm, term=term, value=test_cluster2_name
        )
        test_coexpression_loader.store_feature_groups(
            group=test_cluster3, soterm=soterm, term=term, value=test_cluster3_name
        )
        # check entire cluster1 relationships (not in reverse)
        self.assertTrue(
            Featureprop.objects.filter(
                feature_id=test_feature1.feature_id, type=term, value=test_cluster1_name
            ).exists()
        )
        self.assertTrue(
            Featureprop.objects.filter(
                feature_id=test_feature3.feature_id, type=term, value=test_cluster1_name
            ).exists()
        )
        self.assertTrue(
            Featureprop.objects.filter(
                feature_id=test_feature2.feature_id, type=term, value=test_cluster1_name
            ).exists()
        )
        # check cluster2 relationships
        self.assertTrue(
            Featureprop.objects.filter(
                feature_id=test_feature5.feature_id, type=term, value=test_cluster2_name
            ).exists()
        )
        self.assertTrue(
            Featureprop.objects.filter(
                feature_id=test_feature4.feature_id, type=term, value=test_cluster2_name
            ).exists()
        )
        self.assertFalse(
            Featureprop.objects.filter(
                feature_id=test_feature6.feature_id, type=term, value=test_cluster3_name
            ).exists()
        )
