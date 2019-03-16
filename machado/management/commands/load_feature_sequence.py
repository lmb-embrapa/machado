# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Load feature sequence file."""

from Bio import SeqIO
from machado.loaders.common import FileValidator
from machado.loaders.exceptions import ImportingError
from machado.loaders.sequence import SequenceLoader
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.core.management.base import BaseCommand, CommandError
from tqdm import tqdm
import os


class Command(BaseCommand):
    """Load feature sequence file."""

    help = 'Load FASTA file and add sequences to existing features'

    def add_arguments(self, parser):
        """Define the arguments."""
        parser.add_argument("--file", help="FASTA File", required=True,
                            type=str)
        parser.add_argument("--soterm", help="SO Sequence Ontology Term (eg. "
                            "chromosome, assembly)", required=True,
                            type=str)
        parser.add_argument("--organism", help="Species name (eg. Homo "
                            "sapiens, Mus musculus)",
                            required=True,
                            type=str)
        parser.add_argument("--cpu", help="Number of threads", default=1,
                            type=int)

    def handle(self,
               file: str,
               soterm: str,
               organism: str,
               verbosity: int = 1,
               cpu: int = 1,
               **options):
        """Execute the main function."""
        if verbosity > 0:
            self.stdout.write('Preprocessing')

        try:
            FileValidator().validate(file)
        except ImportingError as e:
            raise CommandError(e)

        # retrieve only the file name
        filename = os.path.basename(file)
        try:
            sequence_file = SequenceLoader(
                filename=filename,
                organism=organism,
                soterm=soterm)
        except ImportingError as e:
            raise CommandError(e)

        fasta_sequences = SeqIO.parse(open(file), 'fasta')

        pool = ThreadPoolExecutor(max_workers=cpu)
        tasks = list()
        for fasta in fasta_sequences:
            tasks.append(pool.submit(sequence_file.add_sequence_to_feature,
                                     fasta))
        if verbosity > 0:
            self.stdout.write('Loading')
        for task in tqdm(as_completed(tasks), total=len(tasks)):
            if task.result():
                raise(task.result())
        pool.shutdown()

        if verbosity > 0:
            self.stdout.write(self.style.SUCCESS('Done'))
