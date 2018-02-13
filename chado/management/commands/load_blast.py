"""Load FASTA file."""

from Bio.Blast import NCBIXML
from chado.loaders.common import Validator
from chado.loaders.exceptions import ImportingError
from chado.loaders.similarity import SimilarityLoader
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.core.management.base import BaseCommand, CommandError
import os
from tqdm import tqdm


class Command(BaseCommand):
    """Load FASTA file."""

    help = 'Load FASTA file'

    def add_arguments(self, parser):
        """Define the arguments."""
        parser.add_argument("--blast", help="BLAST File", required=True,
                            type=str)
        parser.add_argument("--program", help="Program", required=True,
                            type=str)
        parser.add_argument("--programversion", help="Program version",
                            required=True, type=str)
        parser.add_argument("--description", help="Description",
                            required=False, type=str)
        parser.add_argument("--algorithm", help="Algorithm",
                            required=False, type=str)
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
            Validator().validate(options.get('blast'))
        except ImportingError as e:
            raise CommandError(e)

        filename = os.path.basename(options.get('blast'))

        try:
            blast_file = SimilarityLoader(
                    filename=filename,
                    algorithm=options.get('algorithm'),
                    description=options.get('description'),
                    program=options.get('program'),
                    programversion=options.get('programversion'))
        except ImportingError as e:
            raise CommandError(e)

        blast_records = NCBIXML.parse(open(options.get('blast')))

        cpu = options.get('cpu')
        pool = ThreadPoolExecutor(max_workers=cpu)
        tasks = list()
        for record in blast_records:
            if len(record.alignments) > 0:
                tasks.append(pool.submit(blast_file.store_bio_blast_record,
                                         record))
        if verbosity > 0:
            self.stdout.write('Loading')
        for task in tqdm(as_completed(tasks), total=len(tasks)):
            try:
                task.result()
            except ImportingError as e:
                raise CommandError(e)

        self.stdout.write(self.style.SUCCESS('Done'))
