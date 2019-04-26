# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Analysis."""

from datetime import datetime
from typing import Union

from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError

from machado.loaders.common import retrieve_organism, retrieve_feature_id
from machado.loaders.exceptions import ImportingError
from machado.models import Analysis, Analysisfeature, Analysisprop
from machado.models import Assay, Acquisition, Quantification
from machado.models import Cvterm, Db, Dbxref, Organism, Feature


class AnalysisLoader(object):
    """Load Analysis data."""

    help = "Load analysis records."

    def __init__(self) -> None:
        """Execute the init function."""
        self.cvterm_contained_in = Cvterm.objects.get(
            name="contained in", cv__name="relationship"
        )

    def store_analysis(
        self,
        program: str,
        sourcename: str,
        programversion: str,
        filename: str = None,
        timeexecuted: str = None,
        algorithm: str = None,
        name: str = None,
        description: str = None,
    ) -> Analysis:
        """Store analysis."""
        if isinstance(timeexecuted, str):
            # format is mandatory, e.g.: Oct-16-2016)
            # in settings.py set USE_TZ = False
            try:
                date_format = "%b-%d-%Y"
                timeexecuted = datetime.strptime(timeexecuted, date_format)
            except IntegrityError as e:
                raise ImportingError(e)
        else:
            timeexecuted = datetime.now()
        # create assay object
        try:
            analysis = Analysis.objects.create(
                algorithm=algorithm,
                name=name,
                description=description,
                sourcename=sourcename,
                program=program,
                programversion=programversion,
                timeexecuted=timeexecuted,
            )
            self.store_analysisprop(
                analysis=analysis,
                type_id=self.cvterm_contained_in.cvterm_id,
                value=filename,
            )
        except IntegrityError as e:
            raise ImportingError(e)
        except ObjectDoesNotExist as e:
            raise ImportingError(e)
        return analysis

    def store_analysisprop(
        self, analysis: Analysis, type_id: int, value: str = None, rank: int = 0
    ) -> None:
        """Store analysisprop."""
        try:
            Analysisprop.objects.create(
                analysis=analysis, type_id=type_id, value=value, rank=rank
            )
        except IntegrityError as e:
            raise ImportingError(e)

    def store_quantification(
        self, analysis: Analysis, assayacc: str, assaydb: str = "SRA"
    ) -> None:
        """Store quantification to link assay accession to analysis."""
        # first try to get from Assay dbxref (e.g.: "SRR12345" - from SRA/NCBI)
        try:
            db_assay = Db.objects.get(name=assaydb)
            dbxref_assay = Dbxref.objects.get(accession=assayacc, db=db_assay)
            assay = Assay.objects.get(dbxref=dbxref_assay)
        # then searches name
        except ObjectDoesNotExist:
            assay = Assay.objects.get(name=assayacc)
        # then gives up
        except IntegrityError as e:
            raise ImportingError(e)

        try:
            acquisition = Acquisition.objects.create(assay=assay, name=assayacc)
        except IntegrityError as e:
            raise ImportingError(e)
        try:
            Quantification.objects.create(acquisition=acquisition, analysis=analysis)
        except IntegrityError as e:
            raise ImportingError(e)

    def store_analysisfeature(
        self,
        analysis: Analysis,
        feature: Union[str, Feature],
        organism: Union[str, Organism],
        rawscore: float = None,
        normscore: float = None,
        feature_db: str = "GFF_SOURCE",
        significance: float = None,
        identity: float = None,
    ) -> None:
        """Store analysisfeature (expression counts for a given feature)."""
        if isinstance(organism, Organism):
            pass
        else:
            try:
                organism = retrieve_organism(organism)
            except IntegrityError as e:
                raise ImportingError(e)
        # retrieve feature
        if isinstance(feature, Feature):
            feature_id = feature.feature_id
        else:
            feature_id = retrieve_feature_id(accession=feature, soterm="mRNA")
        # finally create analysisfeature
        try:
            Analysisfeature.objects.create(
                feature_id=feature_id,
                analysis=analysis,
                rawscore=rawscore,
                normscore=normscore,
                significance=significance,
                identity=identity,
            )
        except IntegrityError as e:
            raise ImportingError(e)
