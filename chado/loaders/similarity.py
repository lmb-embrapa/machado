"""Load similarity file."""

from Bio.Blast import Record
from Bio.Blast.Record import HSP
from chado.models import Analysis, Analysisfeature, Feature, Featureloc
from chado.loaders.common import retrieve_ontology_term
from chado.loaders.exceptions import ImportingError
from datetime import datetime, timezone
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
from time import time
from typing import Optional


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

    def store_bio_blast_hsp(self,
                            query_feature: Feature,
                            subject_feature: Feature,
                            hsp: HSP):
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
                                       identity=hsp.identities,
                                       rawscore=hsp.score,
                                       significance=hsp.expect)

        if hsp.query_end < hsp.query_start:
            hsp.query_start, hsp.query_end = hsp.query_end, hsp.query_start
        Featureloc.objects.create(feature=match_part_feature,
                                  srcfeature=query_feature,
                                  fmax=hsp.query_end,
                                  fmin=hsp.query_start,
                                  is_fmax_partial=False,
                                  is_fmin_partial=False,
                                  locgroup=0,
                                  rank=0)

        if hsp.sbjct_end < hsp.sbjct_start:
            hsp.sbjct_start, hsp.sbjct_end = hsp.sbjct_end, hsp.sbjct_start
        Featureloc.objects.create(feature=match_part_feature,
                                  srcfeature=subject_feature,
                                  fmax=hsp.sbjct_end,
                                  fmin=hsp.sbjct_start,
                                  is_fmax_partial=False,
                                  is_fmin_partial=False,
                                  locgroup=0,
                                  rank=1)

    def store_bio_blast_record(self, record: Record):
        """Store bio_blast_record record."""
        try:
            query_id = record.query.split(' ')[0]
            query_feature = Feature.objects.get(
                    uniquename=query_id, type_id=self.so_term_query.cvterm_id)
        except ObjectDoesNotExist as e1:
            try:
                query_id = self.retrieve_id_from_description(record.query)
                query_feature = Feature.objects.get(
                        uniquename=query_id,
                        type_id=self.so_term_query.cvterm_id)
            except ObjectDoesNotExist as e2:
                raise ImportingError(e1, e2)

        for alignment in record.alignments:
            try:
                subject_id = alignment.title.split(' ')[0]
                subject_feature = Feature.objects.get(
                        uniquename=subject_id,
                        type_id=self.so_term_subject.cvterm_id)
            except ObjectDoesNotExist as e1:
                try:
                    subject_id = self.retrieve_id_from_description(
                        alignment.title)
                    subject_feature = Feature.objects.get(
                            uniquename=subject_id,
                            type_id=self.so_term_subject.cvterm_id)
                except ObjectDoesNotExist as e2:
                    raise ImportingError(e1, e2)

            for hsp in alignment.hsps:
                self.store_bio_blast_hsp(
                    query_feature, subject_feature, hsp)
