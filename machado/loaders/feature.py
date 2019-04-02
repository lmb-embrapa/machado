# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Load feature file."""

from machado.models import Cv, Db, Cvterm, Dbxref, Dbxrefprop
from machado.models import Feature, FeatureCvterm, FeatureDbxref, Featureloc
from machado.models import Featureprop, FeatureSynonym
from machado.models import FeatureRelationship, FeatureRelationshipprop
from machado.models import Organism, Pub, PubDbxref, FeaturePub, Synonym
from machado.loaders.common import retrieve_organism
from machado.loaders.exceptions import ImportingError
from datetime import datetime, timezone
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
from pysam.libctabixproxies import GTFProxy
from time import time
from typing import Dict, List, Set, Union
from urllib.parse import unquote
from Bio.SearchIO._model import Hit

# The following features are handled in a specific manner and should not
# be included in VALID_ATTRS: id, name, and parent
VALID_ATTRS = ['dbxref', 'note', 'display', 'alias', 'ontology_term',
               'orf_classification', 'synonym', 'is_circular',
               'gene_synonym', 'description', 'product']


class FeatureLoader(object):
    """Load feature records."""

    help = 'Load feature records.'

    def __init__(self,
                 source: str,
                 filename: str,
                 organism: Union[str, Organism],
                 doi: str = None) -> None:
        """Execute the init function."""
        # initialization of lists/sets to store ignored attributes,
        # ignored goterms, and relationships
        self.cache = {}
        self.usedcache = 0
        self.ignored_attrs: Set[str] = set()
        self.ignored_goterms: Set[str] = set()
        self.relationships: List[Dict[str, str]] = list()
        if isinstance(organism, Organism):
            self.organism = organism
        else:
            try:
                self.organism = retrieve_organism(organism)
            except ObjectDoesNotExist as e:
                raise ImportingError(e)

        try:
            self.db, created = Db.objects.get_or_create(name=source.upper())
            self.filename = filename
        except IntegrityError as e:
            raise ImportingError(e)

        self.db_null, created = Db.objects.get_or_create(name='null')
        null_dbxref, created = Dbxref.objects.get_or_create(
            db=self.db_null, accession='null')
        null_cv, created = Cv.objects.get_or_create(name='null')
        null_cvterm, created = Cvterm.objects.get_or_create(
            cv=null_cv,
            name='null',
            definition='',
            dbxref=null_dbxref,
            is_obsolete=0,
            is_relationshiptype=0)
        self.pub, created = Pub.objects.get_or_create(
            miniref='null',
            uniquename='null',
            type_id=null_cvterm.cvterm_id,
            is_obsolete=False)

        self.cvterm_contained_in = Cvterm.objects.get(
            name='contained in', cv__name='relationship')
        self.aa_cvterm = Cvterm.objects.get(
            name='polypeptide', cv__name='sequence')
        self.so_term_protein_match = Cvterm.objects.get(
            name='protein_match', cv__name='sequence')
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

    def get_attributes(self, attributes: str) -> Dict[str, str]:
        """Get attributes."""
        result = dict()
        fields = attributes.split(";")
        for field in fields:
            key, value = field.split("=")
            result[key.lower()] = unquote(value)
        return result

    def process_attributes(self,
                           feature: object,
                           attrs: Dict[str, str]) -> None:
        """Process the VALID_ATTRS attributes."""
        try:
            cvterm_exact = Cvterm.objects.get(
                name='exact', cv__name='synonym_type')
        except ObjectDoesNotExist as e:
            raise ImportingError(e)

        # Don't forget to add the attribute to the constant VALID_ATTRS
        for key in attrs:
            if key not in VALID_ATTRS:
                continue
            elif key in ['ontology_term']:
                # store in featurecvterm
                terms = attrs[key].split(',')
                for term in terms:
                    try:
                        aux_db, aux_term = term.split(':')
                        term_db = Db.objects.get(name=aux_db.upper())
                        dbxref = Dbxref.objects.get(
                            db=term_db, accession=aux_term)
                        cvterm = Cvterm.objects.get(dbxref=dbxref)
                        FeatureCvterm.objects.create(feature=feature,
                                                     cvterm=cvterm,
                                                     pub=self.pub,
                                                     is_not=False,
                                                     rank=0)
                    except ObjectDoesNotExist:
                        self.ignored_goterms.add(term)
            elif key in ['dbxref']:
                try:
                    dbxrefs = attrs[key].split(',')
                except ValueError as e:
                    raise ImportingError('{}: {}'.format(attrs[key], e))
                for dbxref in dbxrefs:
                    # It expects just one dbxref formated as XX:012345
                    try:
                        aux_db, aux_dbxref = dbxref.split(':')
                    except ValueError as e:
                        raise ImportingError('{}: {}'.format(dbxref, e))
                    db, created = Db.objects.get_or_create(name=aux_db.upper())
                    dbxref, created = Dbxref.objects.get_or_create(
                        db=db, accession=aux_dbxref)
                    FeatureDbxref.objects.create(feature=feature,
                                                 dbxref=dbxref,
                                                 is_current=1)
            elif key in ['alias', 'gene_synonym', 'synonym']:
                synonym, created = Synonym.objects.get_or_create(
                    name=attrs.get(key),
                    defaults={'type_id': cvterm_exact.cvterm_id,
                              'synonym_sgml': attrs.get(key)})
                FeatureSynonym.objects.create(synonym=synonym,
                                              feature=feature,
                                              pub=self.pub,
                                              is_current=True,
                                              is_internal=False)
            else:
                note_dbxref, created = Dbxref.objects.get_or_create(
                    db=self.db_null, accession=key)
                cv_feature_property, created = Cv.objects.get_or_create(
                    name='feature_property')
                note_cvterm, created = Cvterm.objects.get_or_create(
                    cv=cv_feature_property,
                    name=key,
                    dbxref=note_dbxref,
                    defaults={'definition': '',
                              'is_relationshiptype': 0,
                              'is_obsolete': 0})
                featureprop_obj, created = Featureprop.objects.get_or_create(
                    feature=feature, type_id=note_cvterm.cvterm_id, rank=0,
                    defaults={'value': attrs.get(key)})
                if not created:
                    featureprop_obj.value = attrs.get(key)
                    featureprop_obj.save()

    def store_tabix_feature(self, tabix_feature: GTFProxy) -> None:
        """Store tabix feature."""
        attrs = self.get_attributes(tabix_feature.attributes)
        for key in attrs:
            if key not in VALID_ATTRS and key not in ['id', 'name', 'parent']:
                self.ignored_attrs.add(key)

        cvterm = Cvterm.objects.get(
            name=tabix_feature.feature, cv__name='sequence')

        # set id = auto# for features that lack it
        if attrs.get('id') is None:
            attrs['id'] = 'auto{}'.format(str(time()))

        try:
            dbxref, created = Dbxref.objects.get_or_create(
                db=self.db, accession=attrs['id'])
            Dbxrefprop.objects.get_or_create(
                dbxref=dbxref, type_id=self.cvterm_contained_in.cvterm_id,
                value=self.filename, rank=0)
            feature = Feature.objects.create(
                    organism=self.organism,
                    uniquename=attrs.get('id'),
                    type_id=cvterm.cvterm_id,
                    name=attrs.get('name'),
                    dbxref=dbxref,
                    is_analysis=False,
                    is_obsolete=False,
                    timeaccessioned=datetime.now(timezone.utc),
                    timelastmodified=datetime.now(timezone.utc))
        except IntegrityError as e:
            raise ImportingError(
                    'ID {} already registered. {}'.format(attrs.get('id'), e))

        # DOI: try to link feature to publication's DOI
        if (feature and self.pub_dbxref_doi):
            try:
                FeaturePub.objects.get_or_create(
                        feature=feature,
                        pub_id=self.pub_dbxref_doi.pub_id)
            except IntegrityError as e:
                raise ImportingError(e)

        try:
            srcdb = Db.objects.get(name="FASTA_SOURCE")
            srcdbxref = Dbxref.objects.get(accession=tabix_feature.contig,
                                           db=srcdb)
            srcfeature = Feature.objects.get(
                dbxref=srcdbxref, organism=self.organism)
        except ObjectDoesNotExist:
            raise ImportingError(
                "Parent not found: {}. It's required to load "
                "a reference FASTA file before loading features."
                .format(tabix_feature.contig))

        # the database requires -1, 0, and +1 for strand
        if tabix_feature.strand == '+':
            strand = +1
        elif tabix_feature.strand == '-':
            strand = -1
        else:
            strand = 0

        # if row.frame is . phase = None
        # some versions of pysam throws ValueError
        try:
            phase = tabix_feature.frame
            if tabix_feature.frame == '.':
                phase = None
        except ValueError:
            phase = None

        try:
            Featureloc.objects.get_or_create(
                feature=feature,
                srcfeature_id=srcfeature.feature_id,
                fmin=tabix_feature.start,
                is_fmin_partial=False,
                fmax=tabix_feature.end,
                is_fmax_partial=False,
                strand=strand,
                phase=phase,
                locgroup=0,
                rank=0)
        except IntegrityError as e:
            print(feature.uniquename,
                  srcfeature.uniquename,
                  tabix_feature.start,
                  tabix_feature.end,
                  strand,
                  phase)
            raise ImportingError(e)

        self.process_attributes(feature, attrs)

        if attrs.get('parent') is not None:
            self.relationships.append({'object_id': attrs['id'],
                                       'subject_id': attrs['parent']})

        # Additional protrein record for each mRNA with the exact same ID
        if tabix_feature.feature == 'mRNA':
            translation_of = Cvterm.objects.get(
                name='translation_of', cv__name='sequence')
            feature_mRNA_translation = Feature.objects.create(
                    organism=self.organism,
                    uniquename=attrs.get('id'),
                    type_id=self.aa_cvterm.cvterm_id,
                    name=attrs.get('name'),
                    dbxref=dbxref,
                    is_analysis=False,
                    is_obsolete=False,
                    timeaccessioned=datetime.now(timezone.utc),
                    timelastmodified=datetime.now(timezone.utc))
            FeatureRelationship.objects.create(object=feature_mRNA_translation,
                                               subject=feature,
                                               type=translation_of,
                                               rank=0)

    def store_relationships(self) -> None:
        """Store the relationships."""
        part_of = Cvterm.objects.get(name='part_of', cv__name='sequence')
        relationships = list()
        features = Feature.objects.filter(
            organism=self.organism).exclude(type=self.aa_cvterm)
        for item in self.relationships:
            try:
                # the aa features should be excluded since they were created
                # using the same mRNA ID
                object = features.get(uniquename=item['object_id'],
                                      organism=self.organism)
                subject = features.get(uniquename=item['subject_id'],
                                       organism=self.organism)
                relationships.append(FeatureRelationship(
                    subject_id=subject.feature_id,
                    object_id=object.feature_id,
                    type_id=part_of.cvterm_id,
                    rank=0))
            except ObjectDoesNotExist:
                print('Parent/Feature ({}/{}) not registered.'
                      .format(item['object_id'], item['subject_id']))

        FeatureRelationship.objects.bulk_create(relationships)

    def store_bio_searchio_hit(self,
                               searchio_hit: Hit,
                               target: str) -> None:
        """Store bio searchio hit."""
        if not hasattr(searchio_hit, 'accession'):
            searchio_hit.accession = None

        # if interproscan-xml parsing, get db name from Hit.attributes.
        if target == 'InterPro':
            db_name = searchio_hit.attributes['Target'].upper()
            db, created = Db.objects.get_or_create(name=db_name)
        # if blast-xml parsing, db name is self.db ("BLAST_source")
        else:
            db = self.db

        dbxref, created = Dbxref.objects.get_or_create(
            db=db, accession=searchio_hit.id)
        feature, created = Feature.objects.get_or_create(
                organism=self.organism,
                uniquename=searchio_hit.id,
                type_id=self.so_term_protein_match.cvterm_id,
                name=searchio_hit.accession,
                dbxref=dbxref,
                defaults={
                    'is_analysis': False,
                    'is_obsolete': False,
                    'timeaccessioned': datetime.now(timezone.utc),
                    'timelastmodified': datetime.now(timezone.utc)})
        if not created:
            return None

        for aux_dbxref in searchio_hit.dbxrefs:
            aux_db, aux_term = aux_dbxref.split(':')
            if aux_db == 'GO':
                try:
                    term_db = Db.objects.get(name=aux_db.upper())
                    dbxref = Dbxref.objects.get(
                        db=term_db, accession=aux_term)
                    cvterm = Cvterm.objects.get(dbxref=dbxref)
                    FeatureCvterm.objects.get_or_create(
                        feature=feature, cvterm=cvterm, pub=self.pub,
                        is_not=False, rank=0)
                except ObjectDoesNotExist:
                    self.ignored_goterms.add(aux_dbxref)
            else:
                term_db, created = Db.objects.get_or_create(
                    name=aux_db.upper())
                dbxref, created = Dbxref.objects.get_or_create(
                    db=term_db, accession=aux_term)
                FeatureDbxref.objects.get_or_create(
                    feature=feature, dbxref=dbxref, is_current=1)

        return None

    def store_feature_annotation(self,
                                 feature: str,
                                 cvterm: str,
                                 annotation: str) -> None:
        """Store feature annotation."""
        attrs = {cvterm: annotation}
        for key in attrs:
            if key not in VALID_ATTRS:
                self.ignored_attrs.add(key)

        features = Feature.objects.filter(
            organism=self.organism,
            dbxref__accession=feature,
            dbxref__db__name__in=['GFF_SOURCE', 'FASTA_SOURCE'])

        if len(features) == 0:
            raise ImportingError('{} not found.'.format(feature))

        for feature_obj in features:
            self.process_attributes(feature_obj, attrs)

    def store_feature_publication(self,
                                  feature: str,
                                  doi: str) -> None:
        """Store feature publication."""
        features = Feature.objects.filter(
            organism=self.organism,
            dbxref__accession=feature,
            dbxref__db__name__in=['GFF_SOURCE', 'FASTA_SOURCE'])

        if len(features) == 0:
            raise ImportingError('{} not found.'.format(feature))

        try:
            doi_obj = Dbxref.objects.get(accession=doi, db__name='DOI')
            pub_obj = Pub.objects.get(PubDbxref_pub_Pub__dbxref=doi_obj)
        except ObjectDoesNotExist:
            raise ImportingError('{} not registered.', doi)

        for feature_obj in features:
            FeaturePub.objects.get_or_create(
                    feature=feature_obj,
                    pub=pub_obj)

    def store_feature_relationships_group(
                               self,
                               group: list,
                               term: Union[str, Cvterm],
                               value: str = None,
                               ontology: Union[str, Cv] = 'relationship',
                               cache: int = 0
                               ) -> None:
        """Store Feature Relationship Groups."""
        frelationshipsp = list()
        # check if retrieving cvterm is needed
        if isinstance(term, Cvterm):
            cvterm = term
        else:
            cvterm = Cvterm.objects.get(name=term, cv__name=ontology)
        buffer_group = group.copy()
        for member in group:
            try:
                subject_id = self.cache[member]
                self.usedcache += 1
            except KeyError:
                try:
                    subject_id = Feature.objects.get(
                        type__cv__name='sequence',
                        type__name='polypeptide',
                        dbxref__accession=member,
                        dbxref__db__name__in=['GFF_SOURCE',
                                              'FASTA_SOURCE']).feature_id
                    self.cache[member] = subject_id
                except ObjectDoesNotExist:
                    continue
            except IntegrityError as e:
                raise ImportingError(e)
            buffer_group.remove(member)
            for othermember in buffer_group:
                try:
                    object_id = self.cache[othermember]
                except KeyError:
                    try:
                        object_id = Feature.objects.get(
                            type__cv__name='sequence',
                            type__name='polypeptide',
                            dbxref__accession=othermember,
                            dbxref__db__name__in=['GFF_SOURCE',
                                                  'FASTA_SOURCE']).feature_id
                        self.cache[othermember] = object_id
                    except ObjectDoesNotExist:
                        continue
                except IntegrityError as e:
                    raise ImportingError(e)
                try:
                    frelationship = FeatureRelationship.objects.create(
                                            subject_id=subject_id,
                                            object_id=object_id,
                                            type=cvterm,
                                            value=value,
                                            rank=0)
                    frelationshipsp.append(FeatureRelationshipprop(
                            feature_relationship=frelationship,
                            type=self.cvterm_contained_in,
                            value=self.filename,
                            rank=0))
                except IntegrityError as e:
                    raise ImportingError(e)
        FeatureRelationshipprop.objects.bulk_create(frelationshipsp)
