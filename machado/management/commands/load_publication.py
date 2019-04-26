# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Load Publication file."""

from concurrent.futures import ThreadPoolExecutor, as_completed

import bibtexparser
from django.core.management.base import BaseCommand, CommandError

# import os
from tqdm import tqdm

from machado.loaders.common import FileValidator
from machado.loaders.exceptions import ImportingError
from machado.loaders.publication import PublicationLoader


class Command(BaseCommand):
    """Load Publication file."""

    help = "Load Publication file"

    def add_arguments(self, parser):
        """Define the arguments."""
        parser.add_argument("--file", help="BibTeX File", required=True, type=str)
        parser.add_argument("--cpu", help="Number of threads", default=1, type=int)

    def handle(self, file=str, verbosity: int = 1, cpu: int = 1, **options):
        """Execute the main function."""
        if verbosity > 0:
            self.stdout.write("Preprocessing")

        try:
            FileValidator().validate(file)
        except ImportingError as e:
            raise CommandError(e)

        # filename = os.path.basename(file)
        bib_database = None
        try:
            bib_database = bibtexparser.load(open(file))
        except ValueError as e:
            return CommandError(e)

        bibtex = PublicationLoader()

        pool = ThreadPoolExecutor(max_workers=cpu)
        tasks = list()
        for entry in bib_database.entries:
            # create model object for each entry
            if entry["ENTRYTYPE"]:
                tasks.append(pool.submit(bibtex.store_bibtex_entry, entry))
        if verbosity > 0:
            self.stdout.write("Loading")
        for task in tqdm(
            as_completed(tasks),
            total=len(tasks),
            disable=False if verbosity > 0 else True,
        ):
            try:
                task.result()
            except ImportingError as e:
                raise CommandError(e)
        pool.shutdown()

        if verbosity > 0:
            self.stdout.write(self.style.SUCCESS("Done"))
