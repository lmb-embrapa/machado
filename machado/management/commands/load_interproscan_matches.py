# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Load InterproScan matches."""

from machado.loaders.common import FileValidator
from machado.loaders.exceptions import ImportingError
from machado.loaders.feature import FeatureLoader
from machado.models import Organism
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.core.management.base import BaseCommand, CommandError
from tqdm import tqdm
import os
from Bio import SearchIO


class Command(BaseCommand):
    """Load InterproScan matches."""

    help = 'Load InterproScan matches'

    def add_arguments(self, parser):
        """Define the arguments."""
        parser.add_argument("--file", help="InterproScan XML file",
                            required=True, type=str)
        parser.add_argument("--cpu", help="Number of threads", default=1,
                            type=int)

    def handle(self,
               file: str,
               cpu: int = 1,
               verbosity: int = 1,
               **options):
        """Execute the main function."""
        # retrieve only the file name
        try:
            FileValidator().validate(file)
        except ImportingError as e:
            raise CommandError(e)

        organism, created = Organism.objects.get_or_create(
            abbreviation='multispecies', genus='multispecies',
            species='multispecies', common_name='multispecies')

        filename = os.path.basename(file)
        if verbosity > 0:
            self.stdout.write('Processing file: {}'.format(filename))
        try:
            feature_file = FeatureLoader(
                filename=filename,
                source='InterproScan_source',
                organism=organism,
            )
        except ImportingError as e:
            raise CommandError(e)

        try:
            records = SearchIO.parse(file, 'interproscan-xml')
        except ValueError as e:
            return CommandError(e)

        pool = ThreadPoolExecutor(max_workers=cpu)
        tasks = list()
        for record in records:
            for hit in record.hits:
                tasks.append(pool.submit(
                    feature_file.store_bio_searchio_hit, hit))
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
