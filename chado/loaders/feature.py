"""Load GFF file."""

from chado.models import Cv, Db, Cvterm, Dbxref
from chado.models import Feature, FeatureCvterm, FeatureDbxref, Featureloc
from chado.models import Featureprop, FeatureSynonym, FeatureRelationship
from chado.models import Pub, Synonym
from chado.loaders.common import retrieve_ontology_term, retrieve_organism
from chado.loaders.exceptions import ImportingError
from datetime import datetime, timezone
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
from time import time
from urllib.parse import unquote

# The following features are handled in a specific manner and should not
# be included in VALID_ATTRS: id, name, and parent
VALID_ATTRS = ['dbxref', 'note', 'display', 'parent', 'alias', 'ontology_term',
               'gene', 'orf_classification', 'ncrna_class', 'pseudo',
               'product', 'is_circular', 'gene_synonym', 'partial']


class FeatureLoader(object):
    """Load feature file."""

    help = 'Load GFF3 file indexed with tabix.'

    def __init__(self, filename, organism, *args, **kwargs):
        """Execute the main function."""
        # Retrieve organism object
        try:
            self.organism = retrieve_organism(organism)
        except ObjectDoesNotExist as e:
            raise ImportingError(e)

        # Save DB file info
        try:
            self.db = Db.objects.create(name=filename,
                                        description=kwargs.get('description'),
                                        url=kwargs.get('url'))
        except IntegrityError as e:
            raise ImportingError(e)

        # retrieving the pub 'null'
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

        # initialization of lists/sets to store ignored attributes,
        # ignored goterms, and relationships
        self.ignored_attrs = set()
        self.ignored_goterms = set()
        self.relationships = list()

    def get_attributes(self, attributes):
        """Get attributes."""
        # receive a line from tbx.fetch and retreive one of the attribute
        # fields
        result = dict()
        fields = attributes.split(";")
        for field in fields:
            key, value = field.split("=")
            result[key.lower()] = unquote(value)
        return result

    def process_attributes(self, feature, attrs):
        """Process the VALID_ATTRS attributes.

        Args:
            feature: type object
            attrs: type dict
        """
        # retrieving the cvterm 'exact'
        cvterm_exact = retrieve_ontology_term('synonym_type', 'exact')

        # Don't forget to add the attribute to the constant VALID_ATTRS
        for key in attrs:
            if key not in VALID_ATTRS:
                continue
            elif key in ['ontology_term']:
                # store in featurecvterm
                terms = attrs.get(key).split(',')
                for term in terms:
                    try:
                        aux_db, aux_term = term.split(':')
                        term_db = Db.objects.get(name=aux_db)
                        dbxref = Dbxref.objects.get(db=term_db,
                                                    accession=aux_term)
                        cvterm = Cvterm.objects.get(dbxref=dbxref)
                        FeatureCvterm.objects.create(feature=feature,
                                                     cvterm=cvterm,
                                                     pub=self.pub,
                                                     is_not=False,
                                                     rank=0)
                    except ObjectDoesNotExist:
                        self.ignored_goterms.add(term)
            elif key in ['dbxref']:
                dbxrefs = attrs[key].split(',')
                for dbxref in dbxrefs:
                    # It expects just one dbxref formated as XX:012345
                    aux_db, aux_dbxref = dbxref.split(':')
                    # create a dbxref for the column source
                    db, created = Db.objects.get_or_create(name=aux_db)
                    dbxref, created = Dbxref.objects.get_or_create(
                        db=db, accession=aux_dbxref)

                    # associate feature with source
                    FeatureDbxref.objects.create(feature=feature,
                                                 dbxref=dbxref,
                                                 is_current=1)
            elif key in ['alias']:
                # Store in featuresynonym
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
                # Store in featureprop
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
                Featureprop.objects.create(feature=feature,
                                           type_id=note_cvterm.cvterm_id,
                                           value=attrs.get(key),
                                           rank=0)

        return

    def store_tabix_feature(self, tabix_feature):
        """Store tabix feature."""
        # populate tables related to GFF
        attrs = self.get_attributes(tabix_feature.attributes)
        for key in attrs:
            if key not in VALID_ATTRS and key not in ['id', 'name', 'parent']:
                self.ignored_attrs.add(key)

        # Retrieve sequence ontology object
        cvterm = retrieve_ontology_term(ontology='sequence',
                                        term=tabix_feature.feature)

        # set id = auto#
        if attrs.get('id') is None:
            attrs['id'] = 'auto{}'.format(str(time()))

        # creating a dbxref for the feature
        dbxref, created = Dbxref.objects.get_or_create(
            db=self.db, accession=attrs['id'])

        # creating a new feature
        try:
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

        # retrieving the source feature
        try:
            srcfeature = Feature.objects.get(
                uniquename=tabix_feature.contig, organism=self.organism)
        except ObjectDoesNotExist:
            raise ImportingError(
                "Parent not found: %s. It's required to load "
                "a reference FASTA file before loading features."
                % (tabix_feature.contig))

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

        # storing the feature location
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

        # adding attributes to featureprop
        self.process_attributes(feature, attrs)

        # storing the feature and parent ids
        if attrs.get('parent') is not None:
            self.relationships.append((attrs['id'], attrs['parent']))

    def store_relationships(self):
        """Store the relationships."""
        # Retrieve the part_of relations ontology term
        part_of = retrieve_ontology_term(ontology='sequence',
                                         term='part_of')
        # creating the feature relationships
        relationships = list()
        for item in self.relationships:
            try:
                subject = Feature.objects.get(uniquename=item[0],
                                              organism=self.organism)
                object = Feature.objects.get(uniquename=item[1],
                                             organism=self.organism)
                relationships.append(FeatureRelationship(
                    subject_id=subject.feature_id,
                    object_id=object.feature_id,
                    type_id=part_of.cvterm_id,
                    rank=0))
            except ObjectDoesNotExist as e:
                print('Parent/Feature ({}/{}) not registered.'.format(item[0],
                                                                      item[1]))

        FeatureRelationship.objects.bulk_create(relationships)
