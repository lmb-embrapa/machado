"""Load GFF file."""
from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist

import os
import pysam
from urllib.parse import unquote
from datetime import datetime, timezone

from chado.models import Cv, Db, Cvterm, Dbxref
from chado.models import Feature, FeatureCvterm, FeatureDbxref, Featureloc
from chado.models import Featureprop, FeatureRelationship, FeatureSynonym
from chado.models import Organism, Project, ProjectFeature, Pub, Synonym
from chado.loaders.common import get_ontology_term

VALID_ATTRS = ['dbxref', 'note', 'display', 'parent', 'alias', 'ontology_term',
               'gene', 'id', 'name', 'orf_classification']


class Command(BaseCommand):
    """Load GFF file."""

    help = 'Load GFF3 file indexed with tabix.'

    def add_arguments(self, parser):
        """Define the arguments."""
        parser.add_argument("--gff",
                            help="GFF3 genome file indexed with tabix"
                            "(see http://www.htslib.org/doc/tabix.html)",
                            required=True,
                            type=str)
        parser.add_argument("--organism", help="Species name (eg. Homo "
                            "sapiens, Mus musculus)",
                            required=True,
                            type=str)
        parser.add_argument("--description", help="DB Description",
                            required=False, type=str)
        parser.add_argument("--url", help="DB URL", required=False, type=str)
        parser.add_argument("--project", help="Project name", required=False,
                            type=str)

    def get_organism(organism):
        """Retrieve organism object."""
        try:
            aux = organism.split(' ')
            genus = aux[0]
            species = 'spp.'
            infraspecific = None
            if len(aux) == 2:
                species = aux[1]
            elif len(aux) > 2:
                species = aux[1]
                infraspecific = ' '.join(aux[2:])

        except ValueError:
            raise ValueError('The organism genus and species should be '
                             'separated by a single space')

        try:
            organism = Organism.objects.get(species=species,
                                            genus=genus,
                                            infraspecific_name=infraspecific)
        except ObjectDoesNotExist:
            raise ObjectDoesNotExist('%s not registered.'
                                     % organism)
        return organism

    def get_attributes(self, attributes):
        """Get attributes."""
        # receive a line from tbx.fetch and retreive one of the attribute
        # fields (name)
        result = dict()
        fields = attributes.split(";")
        for field in fields:
            key, value = field.split("=")
            result[key.lower()] = unquote(value)
        return result

    def process_attributes(self, project, feature, attrs, pub):
        """Process the VALID_ATTRS attributes.

        Args:
            project: type string
            feature: type object
            attrs: type dict
        """
        # retrieving the cvterm 'exact'
        cvterm_exact = get_ontology_term('synonym_type', 'exact')

        # Don't forget to add the attribute to the constant VALID_ATTRS
        for key in attrs:
            if key in ['id', 'name', 'parent']:
                continue
            elif key in ['note', 'display', 'gene', 'orf_classification']:
                db_null, created = Db.objects.get_or_create(name='null')
                note_dbxref, created = Dbxref.objects.get_or_create(
                    db=db_null, accession=key)
                cv_feature_property, created = Cv.objects.get_or_create(
                    name='feature_property')
                note_cvterm, created = Cvterm.objects.get_or_create(
                    cv=cv_feature_property,
                    name=key,
                    definition='',
                    dbxref=note_dbxref,
                    is_relationshiptype=0)
                Featureprop.objects.create(feature=feature,
                                           type_id=note_cvterm.cvterm_id,
                                           value=attrs.get(key),
                                           rank=0)
            elif key in ['ontology_term']:
                terms = attrs.get(key).split(',')
                for term in terms:
                    term_db, term_id = term.split(':')
                    dbxref = Dbxref.objects.get(db=term_db,
                                                accession=term_id)
                    try:
                        cvterm = Cvterm.objects.get(dbxref=dbxref)
                        FeatureCvterm.objects.create(feature=feature,
                                                     cvterm=cvterm,
                                                     pub=pub,
                                                     is_not=False,
                                                     rank=0)
                    except ObjectDoesNotExist:
                        self.stdout.write(
                            self.style.WARNING('GO term not registered: %s'
                                               % (term)))
            elif key in ['dbxref']:
                dbxrefs = attrs[key].split(',')
                for dbxref in dbxrefs:
                    # It expects just one dbxref formated as XX:012345
                    aux_db, aux_dbxref = dbxref.split(':')
                    # create a dbxref for the column source
                    db, created = Db.objects.get_or_create(name=aux_db)
                    dbxref, created = Dbxref.objects.get_or_create(
                        db=db, accession=aux_dbxref, project=project)

                    # associate feature with source
                    FeatureDbxref.objects.create(feature=feature,
                                                 dbxref=dbxref,
                                                 is_current=1)
            elif key in ['alias']:
                try:
                    synonym = Synonym.objects.get(name=attrs.get(key))
                except ObjectDoesNotExist:
                    synonym = Synonym.objects.create(
                        name=attrs.get(key),
                        type_id=cvterm_exact.cvterm_id,
                        synonym_sgml=attrs.get(key)
                    )
                FeatureSynonym.objects.create(synonym=synonym,
                                              feature=feature,
                                              pub=pub,
                                              is_current=False,
                                              is_internal=False)
        return

    def handle(self, *args, **options):
        """Execute the main function."""
        project = ''
        # retrieve project object
        if options.get('project') is not None:
            project_name = options['project']
            project = Project.objects.get(name=project_name)

        # Retrieve organism object
        organism = self.get_organism(options['organism'])

        # Retrieve the part_of relations ontology term
        part_of = get_ontology_term(ontology='relationship',
                                    term='part_of')

        # Save DB info
        filename = os.path.basename(options['gff'])
        db = Db.objects.create(name=filename,
                               description=options.get('description'),
                               url=options.get('url'))

        # retrieving the pub 'null'
        try:
            pub = Pub.objects.get(uniquename='null')
        except ObjectDoesNotExist:
            db_null, created = Db.objects.get_or_create(name='null')
            null_dbxref, created = Dbxref(db=db_null, accession='null')
            null_cv, created = Cv.objects.get_or_create(name='null')
            null_cvterm, created = Cvterm.objects.get_or_create(
                cv=null_cv,
                name='null',
                definition='',
                dbxref=null_dbxref,
                is_relationshiptype=0)
            pub = Pub.objects.create(miniref='null',
                                     uniquename='null',
                                     type_id=null_cvterm.cvterm_id,
                                     is_obsolete=False)

        # Load the GFF3 file
        auto = 1
        counter = 0
        parents = list()
        ignored_attrs = set()
        with open(options['gff']) as tbx_file:
            # print(str(tbx_file.name))
            tbx = pysam.TabixFile(tbx_file.name)

            # check GFF for anomalies
            # for row in tbx.fetch("chrI", 1, 2000, parser=pysam.asGTF()):
            for row in tbx.fetch(parser=pysam.asGTF()):

                # simple counter status
                counter += 1
                if not counter % 1000:
                    self.stdout.write('%s - %s lines processed.'
                                      % (datetime.now(), counter))

                # populate tables related to GFF
                attrs = self.get_attributes(row.attributes)
                for key in attrs:
                    if key not in VALID_ATTRS:
                        ignored_attrs.add(key)

                # Retrieve sequence ontology object
                cvterm = get_ontology_term(ontology='sequence',
                                           term=row.feature)

                # set id = auto#
                if attrs.get('id') is None:
                    attrs['id'] = 'auto%s' % (auto)
                    auto += 1

                try:
                    feature = Feature.objects.get(uniquename=attrs['id'],
                                                  organism=organism,
                                                  type_id=cvterm.cvterm_id)
                    if feature is not None:
                        self.stdout.write(
                            self.style.WARNING(
                                'Skiping: the feature %s %s is already '
                                'registered.'
                                % (attrs['id'], attrs.get('name'))))
                except ObjectDoesNotExist:

                    # creating a dbxref for the feature
                    db, created = Db.objects.get_or_create(name=db.name)
                    dbxref, created = Dbxref.objects.get_or_create(
                        db=db, accession=attrs['id'], project=project)

                    # creating a new feature
                    feature = Feature.objects.create(
                        dbxref=dbxref,
                        organism=organism,
                        name=attrs.get('name'),
                        uniquename=attrs.get('id'),
                        type_id=cvterm.cvterm_id,
                        is_analysis=False,
                        is_obsolete=False,
                        timeaccessioned=datetime.
                        now(timezone.utc),
                        timelastmodified=datetime.
                        now(timezone.utc)
                    )

                    # retrieving the source feature
                    try:
                        srcfeature = Feature.objects.get(uniquename=row.contig,
                                                         organism=organism)
                    except ObjectDoesNotExist:
                        raise ObjectDoesNotExist(
                            "Parent not found: %s. It's recommended to load "
                            "a reference FASTA file before loading features."
                            % (row.contig))

                    # the database requires -1, 0, and +1 for strand
                    if row.strand == '+':
                        strand = +1
                    elif row.strand == '-':
                        strand = -1
                    else:
                        strand = 0

                    # if row.frame is . phase = None
                    # some versions of pysam throws ValueError
                    try:
                        phase = row.frame
                        if row.frame == '.':
                            phase = None
                    except ValueError:
                        phase = None

                    # storing the feature location
                    Featureloc.objects.create(
                        feature=feature,
                        srcfeature_id=srcfeature.feature_id,
                        fmin=row.start,
                        is_fmin_partial=False,
                        fmax=row.end,
                        is_fmax_partial=False,
                        strand=strand,
                        phase=phase,
                        locgroup=0,
                        rank=0,
                    )

                    # create project_feature
                    if project:
                            ProjectFeature.objects.create(feature=feature,
                                                          project=project)

                    # adding attributes to featureprop
                    self.process_attributes(project, feature, attrs, pub)

                    # storing the feature and parent ids
                    if attrs.get('Parent') is not None:
                        parents.append((attrs['parent'], attrs['id']))

        # creating the feature relationships
        parent_objects = list()
        for parent in parents:
            subject = Feature.objects.get(uniquename=parent[0],
                                          organism=organism)
            object = Feature.objects.get(uniquename=parent[1],
                                         organism=organism)
            parent_objects.append(FeatureRelationship.objects.create(
                subject_id=subject.feature_id,
                object_id=object.feature_id,
                type_id=part_of.cvterm_id,
                rank=0))

        if ignored_attrs is not None:
            self.stdout.write(
                self.style.WARNING('Ignored attrs: %s'
                                   % (ignored_attrs)))

        self.stdout.write(self.style.SUCCESS('%s Done'
                                             % datetime.now()))
