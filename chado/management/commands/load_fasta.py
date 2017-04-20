import hashlib
from datetime import datetime, timezone
from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from chado.models import Feature
from Bio import SeqIO
from chado.lib.dbxref import get_set_dbxref
from chado.lib.organism import get_organism
from chado.lib.db import set_db_file
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
        parser.add_argument("--description", help="DB Description",
                            required=False, type=str)
        parser.add_argument("--url", help="DB URL", required=False, type=str)
        parser.add_argument("--nosequence", help="Don't load the sequence",
                            required=False, action='store_true')

    def handle(self, *args, **options):

        # Retrieve organism object
        organism = get_organism(options['organism'])

        # Save DB file info
        db = set_db_file(file=options['fasta'],
                         description=options.get('description'),
                         url=options.get('url'))

        # Retrieve sequence ontology object
        cvterm = get_ontology_term(ontology='sequence', term=options['soterm'])

        # Loading the fasta file

        fasta_sequences = SeqIO.parse(open(options['fasta']), 'fasta')

        for fasta in fasta_sequences:
            dbxref = get_set_dbxref(db.name, fasta.id, '')

            try:
                feat = Feature.objects.get(uniquename=fasta.id)
                if feat is not None:
                    raise IntegrityError('The sequence %s is already '
                                         'registered.' % fasta.id)
            except ObjectDoesNotExist:
                residues = fasta.seq

                m = hashlib.md5(str(fasta.seq).encode()).hexdigest()
                if options['nosequence']:
                    residues = ''

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
                                             % datetime.now()))
