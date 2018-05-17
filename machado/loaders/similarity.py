# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Load similarity."""

from machado.models import Analysis, Analysisfeature, Feature, Featureloc
from machado.loaders.common import retrieve_ontology_term
from machado.loaders.exceptions import ImportingError
from datetime import datetime, timezone
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
from time import time
from typing import Optional


import warnings
from Bio import BiopythonWarning
warnings.simplefilter('ignore', BiopythonWarning)
with warnings.catch_warnings():
    from Bio.SearchIO._model import query, hsp


class SimilarityLoader(object):
    """Load similarity records."""

    help = 'Load simlarity records.'

    def __init__(self,
                 filename: str,
                 program: str,
                 programversion: str,
                 so_query: str,
                 so_subject: str,
                 algorithm: str=None,
                 name: str=None,
                 description: str=None) -> None:
        """Execute the init function."""
        try:
            self.so_term_query = retrieve_ontology_term(
                    ontology='sequence', term=so_query)
            self.so_term_subject = retrieve_ontology_term(
                    ontology='sequence', term=so_subject)
            self.so_term_match_part = retrieve_ontology_term(
                    ontology='sequence', term='match_part')
            self.analysis = Analysis.objects.create(
                    algorithm=algorithm,
                    name=name,
                    description=description,
                    sourcename=filename,
                    program=program,
                    programversion=programversion,
                    timeexecuted=datetime.now(timezone.utc))
        except IntegrityError as e:
            raise ImportingError(e)
        except ObjectDoesNotExist as e:
            raise ImportingError(e)

    def retrieve_id_from_description(self, description: str) -> Optional[str]:
        """Retrieve ID from description."""
        for item in description.split(' '):
            try:
                key, value = item.split('=')
                if key == 'ID':
                    return value
            except ValueError:
                pass
        return None

    def retrieve_query_from_hsp(
            self, hsp: hsp.HSP) -> Feature:
        """Retrieve the query feature from searchio hsp."""
        try:
            query_feature = Feature.objects.get(
                    uniquename=hsp.query_id,
                    type_id=self.so_term_query.cvterm_id)
        except ObjectDoesNotExist as e1:
            try:
                query_id = self.retrieve_id_from_description(
                        hsp.query_description)
                query_feature = Feature.objects.get(
                        uniquename=query_id,
                        type_id=self.so_term_query.cvterm_id)
            except ObjectDoesNotExist as e2:
                raise ImportingError('Query', e1, e2)

        return query_feature

    def retrieve_subject_from_hsp(
            self, hsp: hsp.HSP) -> Feature:
        """Retrieve the subject feature from searchio hsp."""
        try:
            subject_feature = Feature.objects.get(
                    uniquename=hsp.hit_id,
                    type_id=self.so_term_subject.cvterm_id)
        except ObjectDoesNotExist as e1:
            try:
                subject_id = self.retrieve_id_from_description(
                    hsp.hit_description)
                subject_feature = Feature.objects.get(
                        uniquename=subject_id,
                        type_id=self.so_term_subject.cvterm_id)
            except ObjectDoesNotExist as e2:
                raise ImportingError('Subject', hsp.hit_id, e1, e2)

        return subject_feature

    def store_match_part(self,
                         query_feature: Feature,
                         subject_feature: Feature,
                         identity: float=None,
                         rawscore: float=None,
                         normscore: float=None,
                         significance: float=None,
                         query_start: int=None,
                         query_end: int=None,
                         subject_start: int=None,
                         subject_end: int=None) -> None:
        """Store bio_blast_hsp record."""
        # set id = auto# for match_part features
        match_part_id = 'match_part_{}{}{}'.format(
            str(time()), query_feature.feature_id, subject_feature.feature_id)

        match_part_feature = Feature.objects.create(
                organism=query_feature.organism,
                uniquename=match_part_id,
                type_id=self.so_term_match_part.cvterm_id,
                is_analysis=True,
                is_obsolete=False,
                timeaccessioned=datetime.now(timezone.utc),
                timelastmodified=datetime.now(timezone.utc))

        Analysisfeature.objects.create(analysis=self.analysis,
                                       feature=match_part_feature,
                                       identity=identity,
                                       rawscore=rawscore,
                                       normscore=normscore,
                                       significance=significance)

        if (query_end is not None and
                query_start is not None and
                query_end < query_start):
            query_start, query_end = query_end, query_start
        Featureloc.objects.create(feature=match_part_feature,
                                  srcfeature=query_feature,
                                  fmax=query_end,
                                  fmin=query_start,
                                  is_fmax_partial=False,
                                  is_fmin_partial=False,
                                  locgroup=0,
                                  rank=0)

        if (subject_end is not None and
                subject_start is not None and
                subject_end < subject_start):
            subject_start, subject_end = subject_end, subject_start
        Featureloc.objects.create(feature=match_part_feature,
                                  srcfeature=subject_feature,
                                  fmax=subject_end,
                                  fmin=subject_start,
                                  is_fmax_partial=False,
                                  is_fmin_partial=False,
                                  locgroup=0,
                                  rank=1)

    def store_bio_searchio_query_result(
            self, query_result: query.QueryResult) -> None:
        """Store bio_searchio_query_result."""
        for hsp_item in query_result.hsps:
            query_feature = self.retrieve_query_from_hsp(hsp_item)
            subject_feature = self.retrieve_subject_from_hsp(hsp_item)
            if not hasattr(hsp_item, 'ident_num'):
                hsp_item.ident_num = None
            if not hasattr(hsp_item, 'bitscore'):
                hsp_item.bitscore = None
            if not hasattr(hsp_item, 'bitscore_raw'):
                hsp_item.bitscore_raw = None
            if not hasattr(hsp_item, 'evalue'):
                hsp_item.evalue = None
            self.store_match_part(query_feature=query_feature,
                                  subject_feature=subject_feature,
                                  identity=hsp_item.ident_num,
                                  rawscore=hsp_item.bitscore_raw,
                                  normscore=hsp_item.bitscore,
                                  significance=hsp_item.evalue,
                                  query_start=hsp_item.query_start,
                                  query_end=hsp_item.query_end,
                                  subject_start=hsp_item.hit_start,
                                  subject_end=hsp_item.hit_end)
