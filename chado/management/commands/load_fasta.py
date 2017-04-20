import hashlib
from datetime import datetime, timezone
from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from chado.models import Organism, Cv, Cvterm, Db, Feature
from Bio import SeqIO
from chado.lib.dbxref import get_set_dbxref


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
        parser.add_argument("--description", help="DB Description",
                            required=False, type=str)
        parser.add_argument("--url", help="DB URL", required=False, type=str)
        parser.add_argument("--nosequence", help="Don't load the sequence",
                            required=False, action='store_true')

    def handle(self, *args, **options):

        # Retrieve organism object
        try:
            genus, species = options['organism'].split(' ')
        except ValueError:
            raise ValueError('The organism genus and species should be '
                             'separated by a single space')

        try:
            organism = Organism.objects.get(species=species, genus=genus)
        except ObjectDoesNotExist:
            raise ObjectDoesNotExist('%s not registered.'
                                     % options['organism'])

        # Retrieve sequence ontology object
        try:
            cv = Cv.objects.get(name='sequence')
        except ObjectDoesNotExist:
            raise ObjectDoesNotExist('Sequence Ontology not loaded.')

        # Retrieve sequence ontology term object
        try:
            cvterm = Cvterm.objects.get(cv=cv, name=options['soterm'])
        except ObjectDoesNotExist:
            raise ObjectDoesNotExist('Sequence Ontology term not found.')

        # Save DB info
        try:
            db = Db.objects.get(name=options['fasta'])
            if db is not None:
                raise IntegrityError('The db %s is already registered.'
                                     % db.name)
        except ObjectDoesNotExist:
            Db.objects.create(name=options['fasta'],
                              description=options.get('description'),
                              url=options.get('url'))

        # Loading the fasta file

        db_name = options['fasta']

        fasta_sequences = SeqIO.parse(open(options['fasta']), 'fasta')

        for fasta in fasta_sequences:
            dbxref = get_set_dbxref(db_name, fasta.id, '')

            try:
                feat = Feature.objects.get(uniquename=fasta.id)
                if feat is not None:
                    raise IntegrityError('The sequence %s is already '
                                         'registered.' % fasta.id)
            except ObjectDoesNotExist:
                residues = fasta.seq

                if options['nosequence']:
                    residues = ''
                    m = hashlib.md5(str(fasta.seq).encode()).hexdigest()

                Feature.objects.create(dbxref=dbxref,
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
                                       now(timezone.utc))

        self.stdout.write(self.style.SUCCESS('%s Done'
                                             % datetime.datetime.now()))
