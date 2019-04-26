# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Tests analysis data loader."""

from datetime import datetime

from django.core.management import call_command
from django.test import TestCase

from machado.loaders.analysis import AnalysisLoader
from machado.loaders.assay import AssayLoader
from machado.models import Acquisition, Quantification
from machado.models import Analysis, Analysisfeature, Analysisprop
from machado.models import Cv, Cvterm, Db, Dbxref, Organism
from machado.models import Feature


class AnalysisTest(TestCase):
    """Tests Loaders - AnalysisLoader."""

    help = """Will test with the following sample:

    gene    SRR5167848.htseq        SRR2302912.htseq
    AT2G44195.1.TAIR10  0.0 0.6936967934559419
    AT1G25375.1.TAIR10  2.369615950632963   10.7523002985671
    """

    def test_store_analysis(self):
        """Run Tests ."""
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
        test_term = Cvterm.objects.create(
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

        test_featurename1 = "AT2G44195.1.TAIR10"
        test_featurename2 = "AT1G25375.1.TAIR10"
        # creating test features
        test_feature1 = Feature.objects.create(
            organism=test_organism,
            uniquename=test_featurename1,
            is_analysis=False,
            type_id=test_term.cvterm_id,
            is_obsolete=False,
            timeaccessioned=datetime.now(),
            timelastmodified=datetime.now(),
        )
        test_feature2 = Feature.objects.create(
            organism=test_organism,
            uniquename=test_featurename2,
            is_analysis=False,
            type_id=test_term.cvterm_id,
            is_obsolete=False,
            timeaccessioned=datetime.now(),
            timelastmodified=datetime.now(),
        )
        # Register assay and features to be used
        test_assaydate = "Oct-16-2016"
        test_assaynamedb = "SRA"
        test_assayacc1 = "SRR5167848"
        test_assayacc2 = "SRR2302912"
        test_assayname1 = test_assayacc1
        test_assayname2 = test_assayacc2
        test_filename = "exp.matrix.dummy.txt"
        # register Assays
        test_assay_file = AssayLoader()
        test_assay1 = test_assay_file.store_assay(
            name=test_assayname1,
            filename=test_filename,
            db=test_assaynamedb,
            acc=test_assayacc1,
            assaydate=test_assaydate,
        )
        test_assay2 = test_assay_file.store_assay(
            name=test_assayname2,
            filename=test_filename,
            db=test_assaynamedb,
            acc=test_assayacc2,
            assaydate=test_assaydate,
        )
        # dummy analysis variables
        test_program = "LSTRAP"
        test_programversion = "1.6a"
        test_sourcename1 = test_assayacc1 + ".deSEQ2"
        test_sourcename2 = test_assayacc2 + ".deSEQ2"
        timeexecuted = test_assaydate

        test_analysis_loader = AnalysisLoader()
        test_analysis1 = test_analysis_loader.store_analysis(
            program=test_program,
            programversion=test_programversion,
            sourcename=test_sourcename1,
            timeexecuted=timeexecuted,
            name=test_assayacc1,
            filename=test_filename,
        )
        test_analysis2 = test_analysis_loader.store_analysis(
            program=test_program,
            programversion=test_programversion,
            sourcename=test_sourcename2,
            timeexecuted=timeexecuted,
            name=test_assayacc2,
            filename=test_filename,
        )
        test_analysis_loader.store_quantification(
            analysis=test_analysis1, assayacc=test_assayacc1
        )
        test_analysis_loader.store_quantification(
            analysis=test_analysis2, assayacc=test_assayacc2
        )
        test_analysis_loader.store_analysisfeature(
            analysis=test_analysis1,
            feature=test_featurename1,
            organism=test_organism,
            normscore=0.0,
        )
        test_analysis_loader.store_analysisfeature(
            analysis=test_analysis2,
            feature=test_featurename1,
            organism=test_organism,
            normscore=0.6936967934559419,
        )
        test_analysis_loader.store_analysisfeature(
            analysis=test_analysis1,
            feature=test_featurename2,
            organism=test_organism,
            normscore=2.369615950632963,
        )
        test_analysis_loader.store_analysisfeature(
            analysis=test_analysis2,
            feature=test_featurename2,
            organism=test_organism,
            normscore=10.7523002985671,
        )

        self.assertTrue(
            Analysis.objects.filter(
                name=test_assayacc1,
                program=test_program,
                programversion=test_programversion,
            ).exists()
        )
        self.assertTrue(
            Analysis.objects.filter(
                name=test_assayacc2,
                program=test_program,
                programversion=test_programversion,
            ).exists()
        )
        self.assertTrue(
            Analysisprop.objects.filter(
                analysis=test_analysis1, value=test_filename
            ).exists()
        )
        self.assertTrue(
            Analysisprop.objects.filter(
                analysis=test_analysis2, value=test_filename
            ).exists()
        )
        self.assertTrue(Acquisition.objects.filter(assay=test_assay1).exists())
        self.assertTrue(Acquisition.objects.filter(assay=test_assay2).exists())
        test_acquisition1 = Acquisition.objects.get(assay=test_assay1)
        test_acquisition2 = Acquisition.objects.get(assay=test_assay2)
        self.assertTrue(
            Quantification.objects.filter(
                analysis=test_analysis1, acquisition=test_acquisition1
            ).exists()
        )
        self.assertTrue(
            Quantification.objects.filter(
                analysis=test_analysis2, acquisition=test_acquisition2
            ).exists()
        )
        self.assertTrue(
            Analysisfeature.objects.filter(
                analysis=test_analysis1, feature=test_feature1
            ).exists()
        )
        self.assertTrue(
            Analysisfeature.objects.filter(
                analysis=test_analysis2, feature=test_feature2
            ).exists()
        )
        self.assertTrue(
            Analysisfeature.objects.filter(
                analysis=test_analysis1, feature=test_feature1, normscore=0.0
            ).exists()
        )
        self.assertTrue(
            Analysisfeature.objects.filter(
                analysis=test_analysis2,
                feature=test_feature1,
                normscore=0.6936967934559419,
            ).exists()
        )
        self.assertTrue(
            Analysisfeature.objects.filter(
                analysis=test_analysis1,
                feature=test_feature2,
                normscore=2.369615950632963,
            ).exists()
        )
        self.assertTrue(
            Analysisfeature.objects.filter(
                analysis=test_analysis2,
                feature=test_feature2,
                normscore=10.7523002985671,
            ).exists()
        )
        self.assertTrue(
            Analysisprop.objects.filter(
                analysis=test_analysis1, value="exp.matrix.dummy.txt"
            ).exists()
        )
        self.assertTrue(
            Analysisprop.objects.filter(
                analysis=test_analysis2, value="exp.matrix.dummy.txt"
            ).exists()
        )

        call_command("remove_file", "--name=exp.matrix.dummy.txt", "--verbosity=0")

        self.assertFalse(
            Analysisprop.objects.filter(
                analysis=test_analysis1, value="exp.matrix.dummy.txt"
            ).exists()
        )
        self.assertFalse(
            Analysisprop.objects.filter(
                analysis=test_analysis2, value="exp.matrix.dummy.txt"
            ).exists()
        )
        self.assertFalse(
            Analysis.objects.filter(
                name=test_assayacc1,
                program=test_program,
                programversion=test_programversion,
            ).exists()
        )
        self.assertFalse(
            Analysis.objects.filter(
                name=test_assayacc2,
                program=test_program,
                programversion=test_programversion,
            ).exists()
        )
        self.assertFalse(
            Analysisprop.objects.filter(
                analysis=test_analysis1, value=test_filename
            ).exists()
        )
        self.assertFalse(
            Analysisprop.objects.filter(
                analysis=test_analysis2, value=test_filename
            ).exists()
        )
        self.assertFalse(Acquisition.objects.filter(assay=test_assay1).exists())
        self.assertFalse(Acquisition.objects.filter(assay=test_assay2).exists())
        self.assertFalse(
            Quantification.objects.filter(
                analysis=test_analysis1, acquisition=test_acquisition1
            ).exists()
        )
        self.assertFalse(
            Quantification.objects.filter(
                analysis=test_analysis2, acquisition=test_acquisition2
            ).exists()
        )
        self.assertFalse(
            Analysisfeature.objects.filter(
                analysis=test_analysis1, feature=test_feature1
            ).exists()
        )
        self.assertFalse(
            Analysisfeature.objects.filter(
                analysis=test_analysis2, feature=test_feature2
            ).exists()
        )
        self.assertFalse(
            Analysisfeature.objects.filter(
                analysis=test_analysis1, feature=test_feature1, normscore=0.0
            ).exists()
        )
        self.assertFalse(
            Analysisfeature.objects.filter(
                analysis=test_analysis2,
                feature=test_feature1,
                normscore=0.6936967934559419,
            ).exists()
        )
        self.assertFalse(
            Analysisfeature.objects.filter(
                analysis=test_analysis1,
                feature=test_feature2,
                normscore=2.369615950632963,
            ).exists()
        )
        self.assertFalse(
            Analysisfeature.objects.filter(
                analysis=test_analysis2,
                feature=test_feature2,
                normscore=10.7523002985671,
            ).exists()
        )
