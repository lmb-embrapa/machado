"""Load FASTA file."""

from Bio import SeqIO
from machado.loaders.common import FileValidator
from machado.loaders.exceptions import ImportingError
from machado.loaders.sequence import SequenceLoader
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.core.management.base import BaseCommand, CommandError
from tqdm import tqdm
import os


class Command(BaseCommand):
    """Load FASTA file."""

    help = 'Load FASTA file'

    def add_arguments(self, parser):
        """Define the arguments."""
        parser.add_argument("--file", help="FASTA File", required=True,
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
        parser.add_argument("--description", help="Description",
                            required=False, type=str)
        parser.add_argument("--url", help="URL",
                            required=False, type=str)
        parser.add_argument("--doi", help="DOI of the article reference to "
                            "this sequence. E.g.: 10.1111/s12122-012-1313-4",
                            required=False, type=str)

    def handle(self,
               file: str,
               organism: str,
               soterm: str,
               nosequence: bool=False,
               cpu: int=1,
               description: str=None,
               url: str=None,
               doi: str=None,
               verbosity: int=1,
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
                soterm=soterm,
                description=description,
                url=url,
                doi=doi)
        except ImportingError as e:
            raise CommandError(e)

        fasta_sequences = SeqIO.parse(open(file), 'fasta')

        pool = ThreadPoolExecutor(max_workers=cpu)
        tasks = list()
        for fasta in fasta_sequences:
            tasks.append(pool.submit(sequence_file.store_biopython_seq_record,
                                     fasta,
                                     nosequence))
        if verbosity > 0:
            self.stdout.write('Loading')
        for task in tqdm(as_completed(tasks), total=len(tasks)):
            if task.result():
                raise(task.result())

        self.stdout.write(self.style.SUCCESS('Done'))
