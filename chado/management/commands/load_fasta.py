import sys
import hashlib
from datetime import datetime, timezone
from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from chado.models import Organism, Cv, Cvterm, Db, Dbxref, Feature
from Bio import SeqIO
import json

from chado.lib.dbxref import *

class Command(BaseCommand):
    help = 'Load FASTA file'

    def add_arguments(self, parser):
        parser.add_argument("--fasta", help="FASTA File", required = True, type=str)
        parser.add_argument("--organism", help="Species name (eg. Homo sapiens, Mus musculus)", required = True, type=str)
        parser.add_argument("--soterm", help="SO Sequence Ontology Term (eg. chromosome, supercontig)", required = True, type=str)
        parser.add_argument("--description", help="DB Description", required = False, type=str)
        parser.add_argument("--url", help="DB URL", required = False, type=str)
        parser.add_argument("--nosequence", help="Don't load the sequence", required = False, action='store_true')


    def handle(self, *args, **options):

        # Retrieve organism object
        try:
            genus, species = options['organism'].split(' ')
        except ValueError:
            self.stdout.write(self.style.ERROR('The organism genus and species should be separated by a single space'))
            sys.exit()

        try:
            organism = Organism.objects.get(species=species, genus=genus)
        except ObjectDoesNotExist:
            self.stdout.write(self.style.ERROR('%s not registered.' % options['organism']))
            sys.exit()

        # Retrieve sequence ontology object
        try:
            cv = Cv.objects.get(name='sequence')
        except ObjectDoesNotExist:
            self.stdout.write(self.style.ERROR('Sequence Ontology not loaded.'))
            sys.exit()

         # Retrieve sequence ontology term object
        try:
            cvterm = Cvterm.objects.get(cv=cv, name=options['soterm'])
        except ObjectDoesNotExist:
            self.stdout.write(self.style.ERROR('Sequence Ontology term not found.'))
            sys.exit()

        # Save DB info
        try:
            db = Db.objects.get(name=options['fasta'])
            if db is not None:
                self.stdout.write(self.style.ERROR('%s already registered.' % db.name))
                sys.exit()
        except ObjectDoesNotExist:
            Db.objects.create(name=options['fasta'],
                              description=options.get('description'),
                              url=options.get('url'))

        # Loading the fasta file

        db_name = options['fasta']

        fasta_sequences = SeqIO.parse(open(options['fasta']),'fasta')

        for fasta in fasta_sequences:
            dbxref = get_set_dbxref(db_name,fasta.id,'')

            try:
                feat = Feature.objects.get(name=fasta.id)
                if feat is not None:
                    self.stdout.write(self.style.ERROR('%s already registered.' % fasta.id))
                    sys.exit()
            except ObjectDoesNotExist:
                if options['nosequence']:
                    Feature.objects.create(dbxref=dbxref,
                                           organism=organism,
                                           name=fasta.description,
                                           uniquename=fasta.id,
                                           seqlen=len(fasta.seq),
                                           md5checksum=hashlib.md5(str(fasta.seq).encode()).hexdigest(),
                                           type_id=cvterm.cvterm_id,
                                           is_analysis=False,
                                           is_obsolete=False,
                                           timeaccessioned=datetime.now(timezone.utc),
                                           timelastmodified=datetime.now(timezone.utc))
                else:
                    Feature.objects.create(dbxref=dbxref,
                                           organism=organism,
                                           name=fasta.description,
                                           uniquename=fasta.id,
                                           residues=fasta.seq,
                                           seqlen=len(fasta.seq),
                                           md5checksum=hashlib.md5(str(fasta.seq).encode()).hexdigest(),
                                           type_id=cvterm.cvterm_id,
                                           is_analysis=False,
                                           is_obsolete=False,
                                           timeaccessioned=datetime.now(timezone.utc),
                                           timelastmodified=datetime.now(timezone.utc))

        self.stdout.write(self.style.SUCCESS('Done'))
