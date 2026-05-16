# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Load feature dbxrefs file."""

import os
from concurrent.futures import ThreadPoolExecutor, as_completed

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError
from machado.management.commands._base import HistoryCommandMixin
from tqdm import tqdm

from machado.loaders.common import FileValidator, retrieve_organism
from machado.loaders.exceptions import ImportingError
from machado.loaders.feature import FeatureLoader


class Command(HistoryCommandMixin, BaseCommand):
    """Load feature annotation file."""

    help = "Load database cross-references (DBxRefs) for features from a tab-separated file"

    def add_arguments(self, parser):
        """Define the arguments."""
        parser.add_argument(
            "--file",
            help="Path to the tab-separated file (format: feature.dbxref\tdb:dbxref)",
            required=True,
            type=str,
        )
        parser.add_argument(
            "--organism",
            help="Scientific name of the species (e.g., Homo sapiens)",
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
        parser.add_argument(
            "--ignorenotfound",
            help="Continue processing if a feature is not found",
            required=False,
            action="store_true",
        )

    def handle(
        self,
        file: str,
        organism: str,
        soterm: str,
        verbosity: int = 1,
        cpu: int = 1,
        ignorenotfound: bool = False,
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
            filename=filename, source="GFF_source", organism=organism
        )
        pool = ThreadPoolExecutor(max_workers=cpu)
        tasks = list()
        not_found = list()

        # Load the dbxrefs file
        with open(file) as tab_file:
            for line in tab_file:
                feature, dbxref = line.strip().split("\t")
                tasks.append(
                    pool.submit(
                        feature_file.store_feature_dbxref, feature, soterm, dbxref
                    )
                )

        if verbosity > 0:
            self.stdout.write("Loading data...")

        for task in tqdm(as_completed(tasks), total=len(tasks), disable=verbosity == 0):
            try:
                task.result()
            except ObjectDoesNotExist as e:
                not_found.append(e)
                if not ignorenotfound:
                    raise CommandError(e)
            except ImportingError as e:
                raise CommandError(e)
        pool.shutdown()

        if verbosity > 0:
            self.stdout.write("List of features not found:")
            for item in not_found:
                self.stdout.write("- {}\n".format(item))

        if verbosity > 0:
            self.stdout.write(
                self.style.SUCCESS("Successfully processed {}".format(filename))
            )
