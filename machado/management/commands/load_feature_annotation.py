# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Load feature annotation file."""

import os
from concurrent.futures import ThreadPoolExecutor, as_completed

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError
from tqdm import tqdm

from machado.loaders.common import FileValidator, retrieve_organism
from machado.loaders.exceptions import ImportingError
from machado.loaders.feature import FeatureLoader


class Command(BaseCommand):
    """Load feature annotation file."""

    help = "Load two-column tab separated file containing feature name and "
    "annotation. Current annotation will be replaced."

    def add_arguments(self, parser):
        """Define the arguments."""
        parser.add_argument(
            "--file",
            help="Two-column tab separated file. (feature.dbxref\\tannotation text)",
            required=True,
            type=str,
        )
        parser.add_argument(
            "--organism",
            help="Species name (eg. Homo sapiens, Mus musculus)",
            required=True,
            type=str,
        )
        parser.add_argument(
            "--soterm",
            help="SO Sequence Ontology Term (eg. mRNA, polypeptide)",
            required=True,
            type=str,
        )
        parser.add_argument(
            "--cvterm",
            help="cvterm.name from cv "
            "feature_property. (eg. display, note, product, "
            "alias, ontology_term, annotation)",
            required=True,
            type=str,
        )
        parser.add_argument(
            "--doi",
            help="DOI of the article reference to "
            "this sequence. E.g.: 10.1111/s12122-012-1313-4",
            required=False,
            type=str,
        )
        parser.add_argument("--cpu", help="Number of threads", default=1, type=int)
        parser.add_argument(
            "--ignorenotfound",
            help="Don't raise error and exit if feature not found",
            required=False,
            action="store_true",
        )

    def handle(
        self,
        file: str,
        organism: str,
        cvterm: str,
        soterm: str,
        doi: str = None,
        verbosity: int = 1,
        cpu: int = 1,
        ignorenotfound: bool = False,
        **options,
    ):
        """Execute the main function."""
        if verbosity > 0:
            self.stdout.write("Preprocessing")

        try:
            FileValidator().validate(file)
        except ImportingError as e:
            raise CommandError(e)

        try:
            organism = retrieve_organism(organism)
        except IntegrityError as e:
            raise ImportingError(e)

        # retrieve only the file name
        filename = os.path.basename(file)

        try:
            feature_file = FeatureLoader(
                filename=filename, source="GFF_source", organism=organism
            )
        except ImportingError as e:
            raise CommandError(e)

        pool = ThreadPoolExecutor(max_workers=cpu)
        tasks = list()
        not_found = list()

        # Load the annotation file
        with open(file) as tab_file:
            for line in tab_file:
                if line.startswith("#"):
                    continue
                feature, annotation = line.strip().split("\t")
                tasks.append(
                    pool.submit(
                        feature_file.store_feature_annotation,
                        feature,
                        soterm,
                        cvterm,
                        annotation,
                        doi,
                    )
                )

        if verbosity > 0:
            self.stdout.write("Loading feature annotations")

        for task in tqdm(as_completed(tasks), total=len(tasks)):
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
                self.stdout.write(f"{item}\n")

        if verbosity > 0:
            self.stdout.write(self.style.SUCCESS("Done"))
