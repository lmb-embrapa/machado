# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Load organism publication file."""

from concurrent.futures import ThreadPoolExecutor, as_completed

from django.core.management.base import BaseCommand, CommandError
from tqdm import tqdm

from machado.loaders.common import FileValidator
from machado.loaders.exceptions import ImportingError
from machado.loaders.organism import OrganismLoader


class Command(BaseCommand):
    """Load organism publication file."""

    help = "Load two-column tab separated file containing organism and "
    "publication DOI."

    def add_arguments(self, parser):
        """Define the arguments."""
        parser.add_argument(
            "--file",
            help="Two-column tab separated file. "
            "(organism.dbxref\\tpublication DOI)",
            required=True,
            type=str,
        )
        parser.add_argument("--cpu", help="Number of threads", default=1, type=int)

    def handle(self, file: str, verbosity: int = 1, cpu: int = 1, **options):
        """Execute the main function."""
        if verbosity > 0:
            self.stdout.write("Preprocessing")

        try:
            FileValidator().validate(file)
        except ImportingError as e:
            raise CommandError(e)

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
            self.stdout.write("Loading organism publications")
        for task in tqdm(as_completed(tasks), total=len(tasks)):
            try:
                task.result()
            except ImportingError as e:
                raise CommandError(e)
        pool.shutdown()

        if verbosity > 0:
            self.stdout.write(self.style.SUCCESS("Done"))
