import hashlib
import os
from datetime import datetime, timezone
from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from chado.models import Db, Dbxref, Feature, Organism, Project, ProjectFeature
from Bio import SeqIO
from chado.lib.cvterm import get_ontology_term


class Command(BaseCommand):
    help = 'Load FASTA file'

    def add_arguments(self, parser):
        parser.add_argument("--fasta", help="FASTA File", required=True,
                            type=str)
        parser.add_argument("--organism", help="Species name (eg. Homo "
                            "sapiens, Mus musculus)", required=True, type=str)
        parser.add_argument("--soterm", help="SO Sequence Ontology Term (eg. "
                            "chromosome, supercontig)", required=True,
                            type=str)
        parser.add_argument("--project", help="Project name", required=False,
                            type=str)
        parser.add_argument("--description", help="DB Description",
                            required=False, type=str)
        parser.add_argument("--url", help="DB URL", required=False, type=str)
        parser.add_argument("--nosequence", help="Don't load the sequence",
                            required=False, action='store_true')

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

    def handle(self, *args, **options):

        project = ''
        # retrieve project object
        if options['project']:
            project_name = options['project']
            project = Project.objects.get(name=project_name)

        # Retrieve organism object
        organism = self.get_organism(options['organism'])

        # Save DB file info
        filename = os.path.basename(options['fasta'])
        db = Db.objects.create(name=filename,
                               description=options.get('description'),
                               url=options.get('url'))

        # Retrieve sequence ontology object
        cvterm = get_ontology_term(ontology='sequence', term=options['soterm'])

        # Loading the fasta file

        fasta_sequences = SeqIO.parse(open(options['fasta']), 'fasta')

        counter = 0
        feature_list = list()
        for fasta in fasta_sequences:

            # simple counter status
            counter += 1
            if not counter % 1000:
                self.stdout.write('%s - %s lines processed.'
                                  % (datetime.now(), counter))

            db, created = Db.objects.get_or_create(name=db.name)
            dbxref, created = Dbxref.objects.get_or_create(
                db=db, accession=fasta.id, description='', project=project)

            try:
                feature = Feature.objects.get(uniquename=fasta.id)
                if feature is not None:
                    raise IntegrityError('The sequence %s is already '
                                         'registered.' % fasta.id)
            except ObjectDoesNotExist:
                residues = fasta.seq

                m = hashlib.md5(str(fasta.seq).encode()).hexdigest()
                if options['nosequence']:
                    residues = ''

                # storing feature
                feature_list.append(Feature(dbxref=dbxref,
                                            organism=organism,
                                            name=fasta.description,
                                            uniquename=fasta.id,
                                            residues=residues,
                                            seqlen=len(fasta.seq),
                                            md5checksum=m,
                                            type_id=cvterm.cvterm_id,
                                            is_analysis=False,
                                            is_obsolete=False,
                                            timeaccessioned=datetime.
                                            now(timezone.utc),
                                            timelastmodified=datetime.
                                            now(timezone.utc)))

        # bulk_create features
        loaded_features = Feature.objects.bulk_create(feature_list)

        # bulk_create project_feature
        if project:
            project_feature_list = list()
            for feature in loaded_features:
                project_feature_list.append(
                    ProjectFeature(
                        feature=feature,
                        project=project))
            ProjectFeature.objects.bulk_create(project_feature_list)

        self.stdout.write(self.style.SUCCESS('%s Done'
                                             % datetime.now()))
