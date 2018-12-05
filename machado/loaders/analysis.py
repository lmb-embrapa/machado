# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Analysis."""

from machado.loaders.exceptions import ImportingError
from machado.models import Assay, Acquisition, Quantification, Feature
from machado.models import Analysis, Analysisfeature
from machado.models import Db, Dbxref
from django.db.utils import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime


class AnalysisLoader(object):
    """Load Analysis data."""

    help = 'Load analysis records.'

    def __init__(self,
                 filename: str,
                 program: str,
                 programversion: str,
                 timeexecuted: str = None,
                 algorithm: str = None,
                 name: str = None,
                 description: str = None) -> None:
        """Execute the init function."""
        if timeexecuted:
            # format is mandatory, e.g.: Oct-16-2016)
            # in settings.py set USE_TZ = False
            date_format = '%b-%d-%Y'
            timeexecuted = datetime.strptime(timeexecuted, date_format)
        else:
            timeexecuted = datetime.now()

        # create assay object
        try:
            # TODO - implement coexpression analysis
            # self.so_term_coexpression = retrieve_ontology_term(
            #         ontology='relationshiop', term='correlated with')
            self.analysis = Analysis.objects.create(
                    algorithm=algorithm,
                    name=name,
                    description=description,
                    sourcename=filename,
                    program=program,
                    programversion=programversion,
                    timeexecuted=timeexecuted)
        except IntegrityError as e:
            raise ImportingError(e)
        except ObjectDoesNotExist as e:
            raise ImportingError(e)

    def store_quantification(self,
                             assay_acc: str,
                             assay_db: str = "SRA") -> None:
        """Store quantification to link assay accession to analysis."""
        # first try to get from Assay dbxref (e.g.: "SRR12345" - from SRA/NCBI)
        try:
            db_assay = Db.objects.get(name=assay_db)
            dbxref_assay = Dbxref.objects.get(accession=assay_acc,
                                              db=db_assay)
            assay = Assay.objects.get(dbxref=dbxref_assay)
        # then searches name
        except IntegrityError:
            assay = Assay.objects.get(name=assay_acc)
        # then gives up
        except IntegrityError as e:
            raise ImportingError(e)

        try:
            acquisition = Acquisition.objects.create(
                    assay=assay)
        except IntegrityError as e:
            raise ImportingError(e)
        try:
            Quantification.objects.create(
                    acquisition=acquisition,
                    analysis=self.analysis)
        except IntegrityError as e:
            raise ImportingError(e)

    def store_analysisfeature(self,
                              analysis: Analysis,
                              feature_name: str,
                              feature_db: str = "GFF_SOURCE",
                              rawscore: float = None,
                              normscore: float = None,
                              significance: float = None,
                              identity: float = None) -> None:
        """Store analysisfeature (expression counts for a given feature)."""
        # get database for assay (e.g.: "SRA" - from NCBI)
        try:
            db_feature = Db.objects.get(name=feature_db)
            dbxref_feature = Dbxref.objects.get(accession=feature_name,
                                                db=db_feature)
            feature = Feature.objects.get(dbxref=dbxref_feature)
        except IntegrityError:
            feature = Feature.objects.get(uniquename=feature_name)
        except IntegrityError as e:
            raise ImportingError(e)

        try:
            Analysisfeature.objects.create(
                                    feature=feature,
                                    analysis=self.analysis,
                                    rawscore=rawscore,
                                    normscore=normscore,
                                    significance=significance,
                                    identity=identity)
        except IntegrityError as e:
            raise ImportingError(e)
