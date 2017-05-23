from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist

import pysam
from urllib.parse import unquote
from datetime import datetime, timezone

from chado.models import Feature, FeatureDbxref
from chado.models import Featureloc, FeatureRelationship
from chado.lib.cvterm import get_ontology_term, get_set_cvterm
from chado.lib.db import set_db_file
from chado.lib.dbxref import get_set_dbxref
from chado.lib.organism import get_organism
from chado.lib.project import get_project, get_set_project_feature


class Command(BaseCommand):
    help = 'Load GFF3 file indexed with tabix.'

    def add_arguments(self, parser):
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

    def get_attributes(self, attributes):
        # receive a line from tbx.fetch and retreive one of the attribute
        # fields (name)
        result = dict()
        fields = attributes.split(";")
        for field in fields:
            key, value = field.split("=")
            result[key] = unquote(value)
        return result

    def handle(self, *args, **options):

        project = ''
        # retrieve project object
        if options.get('project') is not None:
            project_name = options['project']
            project = get_project(project_name)

        # Retrieve organism object
        organism = get_organism(options['organism'])

        # Retrieve the part_of relations ontology term
        part_of = get_ontology_term(ontology='relationship',
                                    term='part_of')

        # Save DB info
        db = set_db_file(file=options['gff'],
                         description=options.get('description'),
                         url=options.get('url'))

        # Load the GFF3 file
        auto = 1
        parents = list()
        with open(options['gff']) as tbx_file:
            # print(str(tbx_file.name))
            tbx = pysam.TabixFile(tbx_file.name)

            # check GFF for anomalies
            # for row in tbx.fetch("chrI", 1, 2000, parser=pysam.asGTF()):
            for row in tbx.fetch(parser=pysam.asGTF()):
                # populate tables related to GFF
                attrs = self.get_attributes(row.attributes)
                # print(attrs)

                # Retrieve sequence ontology object
                cvterm = get_ontology_term(ontology='sequence',
                                           term=row.feature)

                # set ID = auto#
                if not attrs.get('ID'):
                    attrs['ID'] = 'auto%s' % (auto)
                    auto += 1

                try:
                    feature = Feature.objects.get(uniquename=attrs['ID'],
                                                  organism=organism,
                                                  type_id=cvterm.cvterm_id)
                    if feature is not None:
                        self.stdout.write(
                            self.style.WARNING('The feature %s %s is already '
                                               'registered.'
                                               % (attrs['ID'], attrs['Name'])))
                except ObjectDoesNotExist:

                    # creating a dbxref for the feature
                    dbxref = get_set_dbxref(db_name=db.name,
                                            accession=attrs['ID'],
                                            project=project)

                    # creating a new feature
                    feature = Feature.objects.create(
                        dbxref=dbxref,
                        organism=organism,
                        name=attrs.get('Name'),
                        uniquename=attrs.get('ID'),
                        type_id=cvterm.cvterm_id,
                        is_analysis=False,
                        is_obsolete=False,
                        timeaccessioned=datetime.
                        now(timezone.utc),
                        timelastmodified=datetime.
                        now(timezone.utc)
                    )

                    # storing the feature location
                    srcfeature = Feature.objects.get(uniquename=row.contig)
                    if row.strand == '+':
                        strand = +1
                    elif row.strand == '-':
                        strand = -1
                    else:
                        strand = 0

                    try:
                        phase = row.frame
                    except ValueError:
                        phase = None

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
                            get_set_project_feature(feature=feature,
                                                    project=project)

                    # create a dbxref for the column source
                    dbxref = get_set_dbxref(db_name=db.name,
                                            accession=row.source,
                                            project=project)
                    # associate feature with source
                    FeatureDbxref.objects.create(feature=feature,
                                                 dbxref=dbxref,
                                                 is_current=1)
                    # storing the feature and parent ids
                    if attrs.get('Parent') is not None:
                        parents.append((attrs['Parent'], attrs['ID']))

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

        self.stdout.write(self.style.SUCCESS('%s Done'
                                             % datetime.now()))
