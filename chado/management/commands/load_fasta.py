"""Load FASTA file."""

from Bio import SeqIO
from chado.loaders.common import Validator
from chado.loaders.exceptions import ImportingError
from chado.loaders.sequence import SequenceLoader
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.core.management.base import BaseCommand, CommandError
from tqdm import tqdm
import os


class Command(BaseCommand):
    """Load FASTA file."""

    help = 'Load FASTA file'

    def add_arguments(self, parser):
        """Define the arguments."""
        parser.add_argument("--fasta", help="FASTA File", required=True,
                            type=str)
        parser.add_argument("--organism", help="Species name (eg. Homo "
                            "sapiens, Mus musculus)", required=True, type=str)
        parser.add_argument("--soterm", help="SO Sequence Ontology Term (eg. "
                            "chromosome, supercontig)", required=True,
                            type=str)
        parser.add_argument("--nosequence", help="Don't load the sequence",
                            required=False, action='store_true')
        parser.add_argument("--cpu", help="Number of threads", default=1,
                            type=int)

    def handle(self, *args, **options):
        """Execute the main function."""
        verbosity = 1
        if options.get('verbosity'):
            verbosity = options.get('verbosity')

        if verbosity > 0:
            self.stdout.write('Preprocessing')

        try:
            Validator().validate(options.get('fasta'))
        except ImportingError as e:
            raise CommandError(e)

        # retrieve only the file name
        filename = os.path.basename(options.get('fasta'))
        try:
            sequence_file = SequenceLoader(
                filename=filename,
                organism=options.get('organism'),
                soterm=options.get('soterm'),
                url=options.get('url'),
                description=options.get('description'))
        except ImportingError as e:
            raise CommandError(e)

        fasta_sequences = SeqIO.parse(open(options.get('fasta')), 'fasta')

        cpu = options.get('cpu')
        pool = ThreadPoolExecutor(max_workers=cpu)
        tasks = list()
        for fasta in fasta_sequences:
            tasks.append(pool.submit(sequence_file.store_biopython_seq_record,
                                     fasta,
                                     options.get('nosequence')))
        if verbosity > 0:
            self.stdout.write('Loading')
        for task in tqdm(as_completed(tasks), total=len(tasks)):
            if task.result():
                raise(task.result())

        self.stdout.write(self.style.SUCCESS('Done'))
