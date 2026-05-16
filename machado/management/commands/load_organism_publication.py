# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Load organism publication file."""

from concurrent.futures import ThreadPoolExecutor, as_completed

from django.core.management.base import BaseCommand
from machado.management.commands._base import HistoryCommandMixin
from tqdm import tqdm

from machado.loaders.common import FileValidator
from machado.loaders.organism import OrganismLoader


class Command(HistoryCommandMixin, BaseCommand):
    """Load organism publication file."""

    help = "Load organism-publication associations from a tab-separated file"

    def add_arguments(self, parser):
        """Define the arguments."""
        parser.add_argument(
            "--file",
            help="Path to the tab-separated file (format: organism_id\\tDOI)",
            required=True,
            type=str,
        )
        parser.add_argument(
            "--cpu",
            help="Number of threads for parallel processing",
            default=1,
            type=int,
        )

    def handle(self, file: str, verbosity: int = 1, cpu: int = 1, **options):
        """Execute the main function."""
        if verbosity > 0:
            self.stdout.write("Preprocessing data...")

        FileValidator().validate(file)
        pool = ThreadPoolExecutor(max_workers=cpu)
        tasks = list()

        # Load the publication file
        with open(file) as tab_file:
            for line in tab_file:
                organism, doi = line.strip().split("\t")
                tasks.append(
                    pool.submit(
                        OrganismLoader().store_organism_publication, organism, doi
                    )
                )

        if verbosity > 0:
            self.stdout.write("Loading data...")
        for task in tqdm(as_completed(tasks), total=len(tasks), disable=verbosity == 0):
            task.result()
        pool.shutdown()

        if verbosity > 0:
            self.stdout.write(self.style.SUCCESS("Operation completed successfully."))
