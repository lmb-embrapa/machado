# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Load organism file."""

import re
from concurrent.futures import ThreadPoolExecutor, as_completed

from django.core.management.base import BaseCommand
from machado.management.commands._base import HistoryCommandMixin
from tqdm import tqdm

from machado.loaders.common import FileValidator
from machado.loaders.organism import OrganismLoader


class Command(HistoryCommandMixin, BaseCommand):
    """Load organism file."""

    help = "Load taxonomy data from an NCBI-style names.dmp file"

    def add_arguments(self, parser):
        """Define the arguments."""
        parser.add_argument(
            "--file",
            help="Path to the names file (e.g., names.dmp)",
            required=True,
            type=str,
        )
        parser.add_argument(
            "--name",
            help="Database name (e.g., DB:NCBI_taxonomy)",
            required=True,
            type=str,
        )
        parser.add_argument(
            "--cpu",
            help="Number of threads for parallel processing",
            default=1,
            type=int,
        )

    def handle(self, file: str, name: str, verbosity: int = 1, cpu: int = 1, **options):
        """Execute the main function."""
        if verbosity > 0:
            self.stdout.write("Preprocessing data...")

        FileValidator().validate(file)
        organism_db = OrganismLoader(organism_db=name)
        file_names = open(file)

        pool = ThreadPoolExecutor(max_workers=cpu)
        tasks = list()
        current_id = None
        taxid, scname = "", ""
        synonyms, common_names = [], []
        for line in file_names:
            columns = re.split(r"\s\|\s", line)
            if current_id is not None and current_id != columns[0]:
                # store if new record
                tasks.append(
                    pool.submit(
                        organism_db.store_organism_record,
                        taxid,
                        scname,
                        synonyms,
                        common_names,
                    )
                )
                taxid, scname = "", ""
                synonyms, common_names = [], []

            current_id = columns[0]

            # get data while current_id remains unchanged
            if columns[3] == "scientific name":
                taxid = columns[0]
                if columns[2] == "" or columns[1] == columns[2]:
                    scname = columns[1]
                else:
                    scname = "{} {}".format(columns[1], columns[2])
            elif columns[3] == "synonym":
                synonyms.append(columns[1])
            elif columns[3] == "common name":
                common_names.append(columns[1])
        else:
            # insert the last record
            tasks.append(
                pool.submit(
                    organism_db.store_organism_record,
                    taxid,
                    scname,
                    synonyms,
                    common_names,
                )
            )

        if verbosity > 0:
            self.stdout.write("Loading data...")
        for task in tqdm(as_completed(tasks), total=len(tasks), disable=verbosity == 0):
            if task.result():
                e = task.result()
                raise (e)
        pool.shutdown()
        if verbosity > 0:
            self.stdout.write(
                self.style.SUCCESS("Successfully processed taxonomy data.")
            )
