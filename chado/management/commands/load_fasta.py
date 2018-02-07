"""Load FASTA file."""

from Bio import SeqIO
from chado.loaders.common import Validator
from chado.loaders.sequence import SequenceLoader
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.core.management.base import BaseCommand
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
        parser.add_argument("--description", help="DB Description",
                            required=False, type=str)
        parser.add_argument("--url", help="DB URL", required=False, type=str)
        parser.add_argument("--nosequence", help="Don't load the sequence",
                            required=False, action='store_true')
        parser.add_argument("--cpu", help="Number of threads", default=1,
                            type=int)

    def handle(self, *args, **options):
        """Execute the main function."""
        verbosity = 1
        if options.get('verbosity'):
            verbosity = options.get('verbosity')

        Validator().validate(options.get('fasta'))

        # retrieve only the file name
        filename = os.path.basename(options.get('fasta'))
        sequence_file = SequenceLoader(
            file=filename,
            organism=options.get('organism'),
            soterm=options.get('soterm'),
            url=options.get('url'),
            description=options.get('description'))

        fasta_sequences = SeqIO.parse(open(options.get('fasta')), 'fasta')

        cpu = options.get('cpu')
        pool = ThreadPoolExecutor(max_workers=cpu)
        tasks = list()
        if verbosity > 0:
            self.stdout.write('Preprocessing')
        for fasta in fasta_sequences:
            tasks.append(pool.submit(sequence_file.store_sequence,
                                     fasta,
                                     options.get('nosequence')))
        if verbosity > 0:
            self.stdout.write('Loading')
        for task in tqdm(as_completed(tasks), total=len(tasks)):
            if task.result():
                raise(task.result())

        self.stdout.write(self.style.SUCCESS('Done'))
