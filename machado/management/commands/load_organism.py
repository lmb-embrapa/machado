# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Load organism file."""

import re
from concurrent.futures import ThreadPoolExecutor, as_completed

from django.core.management.base import BaseCommand, CommandError
from tqdm import tqdm

from machado.loaders.common import FileValidator
from machado.loaders.exceptions import ImportingError
from machado.loaders.organism import OrganismLoader


class Command(BaseCommand):
    """Load organism file."""

    help = "Load organism file"

    def add_arguments(self, parser):
        """Define the arguments."""
        parser.add_argument(
            "--file", help="names file <e.g.: names.dmp>", required=True, type=str
        )
        parser.add_argument(
            "--name", help="DB name <e.g.: DB:NCBI_taxonomy>", required=True, type=str
        )
        parser.add_argument("--cpu", help="Number of threads", default=1, type=int)

    def handle(self, file: str, name: str, verbosity: int = 1, cpu: int = 1, **options):
        """Execute the main function."""
        if verbosity > 0:
            self.stdout.write("Preprocessing")

        try:
            FileValidator().validate(file)
        except ImportingError as e:
            raise CommandError(e)

        try:
            organism_db = OrganismLoader(organism_db=name)
        except ImportingError as e:
            raise CommandError(e)

        file_names = open(file)

        pool = ThreadPoolExecutor(max_workers=cpu)
        tasks = list()
        current_id = None
        taxid, scname = "", ""
        synonyms, common_names = [], []
        for line in file_names:
            columns = re.split("\s\|\s", line)
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
            self.stdout.write("Loading names file")
        for task in tqdm(as_completed(tasks), total=len(tasks)):
            if task.result():
                raise (task.result())
        pool.shutdown()
        if verbosity > 0:
            self.stdout.write(self.style.SUCCESS("Done"))
