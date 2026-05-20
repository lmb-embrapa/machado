# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Load Similarity matches."""

import os
import warnings
from concurrent.futures import ThreadPoolExecutor, as_completed

from Bio import BiopythonWarning
from Bio import SearchIO
from django.core.management.base import BaseCommand, CommandError
from machado.management.commands._base import HistoryCommandMixin
from tqdm import tqdm

from machado.loaders.common import FileValidator
from machado.loaders.feature import MultispeciesFeatureLoader

warnings.simplefilter("ignore", BiopythonWarning)
# with warnings.catch_warnings():
#     from Bio.SearchIO._model import query, hsp


class Command(HistoryCommandMixin, BaseCommand):
    """Load similarity multispecies matches."""

    help = "Load similarity multispecies matches from BLAST or InterproScan XML files"

    def add_arguments(self, parser):
        """Define the arguments."""
        parser.add_argument(
            "--file",
            help="Path to the BLAST or InterproScan XML file",
            required=True,
            type=str,
        )
        parser.add_argument(
            "--format", help="blast-xml or interproscan-xml", required=True, type=str
        )
        parser.add_argument(
            "--cpu",
            help="Number of threads for parallel processing",
            default=1,
            type=int,
        )

    def handle(
        self, file: str, format: str, cpu: int = 1, verbosity: int = 1, **options
    ):
        """Execute the main function."""
        # retrieve only the file name
        FileValidator().validate(file)
        if format == "blast-xml":
            source = "BLAST_source"
        elif format == "interproscan-xml":
            source = "InterproScan_source"
        else:
            raise CommandError(
                "Invalid format: '{}'. Allowed options are 'blast-xml' or 'interproscan-xml'.".format(
                    format
                )
            )

        filename = os.path.basename(file)
        feature_file = MultispeciesFeatureLoader(filename=filename, source=source)
        if verbosity > 0:
            self.stdout.write("Processing file: {}".format(filename))
        try:
            records = SearchIO.parse(file, format)
        except ValueError as e:
            return CommandError(e)

        pool = ThreadPoolExecutor(max_workers=cpu)
        tasks = list()
        for record in records:
            for hit in record.hits:
                tasks.append(
                    pool.submit(feature_file.store_bio_searchio_hit, hit, record.target)
                )
        if verbosity > 0:
            self.stdout.write("Loading data...")
        for task in tqdm(as_completed(tasks), total=len(tasks), disable=verbosity == 0):
            task.result()
        pool.shutdown()

        if len(feature_file.ignored_goterms) > 0:
            self.stdout.write(
                self.style.WARNING(
                    "Ignored GO terms: {}".format(feature_file.ignored_goterms)
                )
            )
        if verbosity > 0:
            self.stdout.write(
                self.style.SUCCESS("Successfully processed {}".format(filename))
            )
