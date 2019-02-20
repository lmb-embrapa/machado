# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Load Similarity matches."""

from machado.loaders.common import FileValidator
from machado.loaders.exceptions import ImportingError
from machado.loaders.feature import FeatureLoader
from machado.models import Organism
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.core.management.base import BaseCommand, CommandError
from tqdm import tqdm
import os
import warnings
from Bio import SearchIO
from Bio import BiopythonWarning
warnings.simplefilter('ignore', BiopythonWarning)
# with warnings.catch_warnings():
#     from Bio.SearchIO._model import query, hsp


class Command(BaseCommand):
    """Load similarity multispecies matches."""

    help = 'Load similiarity multispecies matches'

    def add_arguments(self, parser):
        """Define the arguments."""
        parser.add_argument("--file", help="BLAST/InterproScan XML file",
                            required=True, type=str)
        parser.add_argument("--format",
                            help="blast-xml or interproscan-xml",
                            required=True, type=str)
        parser.add_argument("--cpu", help="Number of threads", default=1,
                            type=int)

    def handle(self,
               file: str,
               format: str,
               cpu: int = 1,
               verbosity: int = 1,
               **options):
        """Execute the main function."""
        # retrieve only the file name
        try:
            FileValidator().validate(file)
        except ImportingError as e:
            raise CommandError(e)
        if format == 'blast-xml':
            source = 'BLAST_source'
        elif format == 'interproscan-xml':
            source = 'InterproScan_source'
        else:
            raise ("Format allowed options are blast-xml or interproscan-xml"
                   " only, not {}".format(format))

        organism, created = Organism.objects.get_or_create(
            abbreviation='multispecies', genus='multispecies',
            species='multispecies', common_name='multispecies')

        filename = os.path.basename(file)
        if verbosity > 0:
            self.stdout.write('Processing file: {}'.format(filename))
        try:
            feature_file = FeatureLoader(
                filename=filename,
                source=source,
                organism=organism,
            )
        except ImportingError as e:
            raise CommandError(e)

        try:
            records = SearchIO.parse(file, format)
        except ValueError as e:
            return CommandError(e)

        pool = ThreadPoolExecutor(max_workers=cpu)
        tasks = list()
        for record in records:
            for hit in record.hits:
                tasks.append(pool.submit(
                    feature_file.store_bio_searchio_hit, hit, record.target))
        if verbosity > 0:
            self.stdout.write('Loading')
        for task in tqdm(as_completed(tasks), total=len(tasks)):
            try:
                task.result()
            except ImportingError as e:
                raise CommandError(e)

        if len(feature_file.ignored_goterms) > 0:
            self.stdout.write(
                self.style.WARNING('Ignored GO terms: {}'.format(
                    feature_file.ignored_goterms)))

        self.stdout.write(self.style.SUCCESS('Done with {}'.format(filename)))
