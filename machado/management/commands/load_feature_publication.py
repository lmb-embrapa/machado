# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Load feature publication file."""

import os
from concurrent.futures import ThreadPoolExecutor, as_completed

from django.core.management.base import BaseCommand
from machado.management.commands._base import HistoryCommandMixin
from tqdm import tqdm

from machado.loaders.common import FileValidator, retrieve_organism
from machado.loaders.feature import FeatureLoader


class Command(HistoryCommandMixin, BaseCommand):
    """Load feature publication file."""

    help = "Load feature-publication associations from a tab-separated file"

    def add_arguments(self, parser):
        """Define the arguments."""
        parser.add_argument(
            "--file",
            help="Path to the tab-separated file (format: feature_id\\tDOI)",
            required=True,
            type=str,
        )
        parser.add_argument(
            "--organism",
            help="Scientific name of the species (e.g., 'Homo sapiens')",
            required=True,
            type=str,
        )
        parser.add_argument(
            "--soterm",
            help="Sequence Ontology (SO) term (e.g., 'mRNA', 'polypeptide')",
            required=True,
            type=str,
        )
        parser.add_argument(
            "--cpu",
            help="Number of threads for parallel processing",
            default=1,
            type=int,
        )

    def handle(
        self,
        file: str,
        organism: str,
        soterm: str,
        verbosity: int = 1,
        cpu: int = 1,
        **options,
    ):
        """Execute the main function."""
        if verbosity > 0:
            self.stdout.write("Preprocessing data...")

        FileValidator().validate(file)
        organism = retrieve_organism(organism)

        # retrieve only the file name
        filename = os.path.basename(file)

        feature_file = FeatureLoader(
            filename=filename, source="PUBLICATION", organism=organism
        )
        pool = ThreadPoolExecutor(max_workers=cpu)
        tasks = list()

        # Load the publication file
        with open(file) as tab_file:
            for line in tab_file:
                feature, doi = line.strip().split("\t")
                tasks.append(
                    pool.submit(
                        feature_file.store_feature_publication, feature, soterm, doi
                    )
                )

        if verbosity > 0:
            self.stdout.write("Loading data...")
        for task in tqdm(as_completed(tasks), total=len(tasks), disable=verbosity == 0):
            task.result()
        pool.shutdown()

        if verbosity > 0:
            self.stdout.write(self.style.SUCCESS("Operation completed successfully."))
