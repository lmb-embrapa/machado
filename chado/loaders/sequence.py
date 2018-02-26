"""Sequence."""

from Bio.SeqRecord import SeqRecord
from chado.loaders.common import retrieve_organism, retrieve_ontology_term
from chado.loaders.exceptions import ImportingError
from chado.models import Db, Dbxref, Dbxrefprop, Feature, FeaturePub, PubDbxref
from datetime import datetime, timezone
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
from hashlib import md5


class SequenceLoader(object):
    """Load sequence records."""

    def __init__(self,
                 filename: str,
                 organism: str,
                 soterm: str,
                 doi: str=None,
                 description: str=None,
                 url: str=None) -> None:
        """Execute the init function."""
        # Retrieve organism object
        try:
            self.organism = retrieve_organism(organism)
        except ObjectDoesNotExist as e:
            raise ImportingError(e)

        # Save DB file info
        try:
            self.db = Db.objects.create(name=filename,
                                        description=description,
                                        url=url)
            self.filename = filename
        except IntegrityError as e:
            raise ImportingError(e)

        # Retrieve sequence ontology object
        self.soterm = retrieve_ontology_term(ontology='sequence',
                                             term=soterm)
        self.cvterm_contained_in = retrieve_ontology_term(
            ontology='relationship', term='contained in')

        # Retrieve DOI's Dbxref
        dbxref_doi = None
        self.pub_dbxref_doi = None
        if doi:
            try:
                dbxref_doi = Dbxref.objects.get(accession=doi)
            except ObjectDoesNotExist as e:
                raise ImportingError(e)
            try:
                self.pub_dbxref_doi = PubDbxref.objects.get(dbxref=dbxref_doi)
            except ObjectDoesNotExist as e:
                raise ImportingError(e)

    def store_biopython_seq_record(self,
                                   seq_obj: SeqRecord,
                                   ignore_residues: bool=False) -> None:
        """Store Biopython SeqRecord."""
        try:
            dbxref = Dbxref.objects.create(
                db=self.db, accession=seq_obj.id)
            Dbxrefprop.objects.create(
                dbxref=dbxref, type_id=self.cvterm_contained_in.cvterm_id,
                value=self.filename, rank=0)
            feature = Feature.objects.get(uniquename=seq_obj.id)
            if feature is not None:
                raise ImportingError('The sequence {} is already '
                                     'registered.'.format(seq_obj.id))
        except ObjectDoesNotExist:
            residues = seq_obj.seq

            m = md5(str(seq_obj.seq).encode()).hexdigest()
            if ignore_residues is True:
                residues = ''

            # storing feature
            feature = Feature(dbxref=dbxref,
                              organism=self.organism,
                              name=seq_obj.description,
                              uniquename=seq_obj.id,
                              residues=residues,
                              seqlen=len(seq_obj.seq),
                              md5checksum=m,
                              type_id=self.soterm.cvterm_id,
                              is_analysis=False,
                              is_obsolete=False,
                              timeaccessioned=datetime.
                              now(timezone.utc),
                              timelastmodified=datetime.
                              now(timezone.utc))
            feature.save()

            # DOI: try to link sequence to publication's DOI
            if (feature and self.pub_dbxref_doi):
                try:
                    FeaturePub.objects.create(
                            feature=feature,
                            pub_id=self.pub_dbxref_doi.pub_id)
                except IntegrityError as e:
                    raise ImportingError(e)
