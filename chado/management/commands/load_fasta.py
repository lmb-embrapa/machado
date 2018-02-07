"""Load FASTA file."""

from Bio import SeqIO
from chado.loaders.common import Validator
from chado.loaders.sequence import SequenceLoader
from django.core.management.base import BaseCommand
from tqdm import tqdm


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

    def handle(self, *args, **options):
        """Execute the main function."""
        Validator().validate(options.get('fasta'))

        sequence_file = SequenceLoader(
            file=options.get('fasta'),
            organism=options.get('organism'),
            soterm=options.get('soterm'),
            url=options.get('url'),
            description=options.get('description'))

        fasta_sequences = SeqIO.parse(open(options.get('fasta')), 'fasta')

        for fasta in tqdm(fasta_sequences, unit=' sequences'):
            sequence_file.store_sequence(fasta, options.get('nosequence'))

        self.stdout.write(self.style.SUCCESS('Done'))
