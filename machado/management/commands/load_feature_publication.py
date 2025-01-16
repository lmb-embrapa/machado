# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Load feature publication file."""

import os
from concurrent.futures import ThreadPoolExecutor, as_completed

from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError
from tqdm import tqdm

from machado.loaders.common import FileValidator, retrieve_organism
from machado.loaders.exceptions import ImportingError
from machado.loaders.feature import FeatureLoader
from machado.models import History


class Command(BaseCommand):
    """Load feature publication file."""

    help = "Load two-column tab separated file containing feature name and "
    "publication DOI."

    def add_arguments(self, parser):
        """Define the arguments."""
        parser.add_argument(
            "--file",
            help="Two-column tab separated file. (feature.dbxref\\tpublication DOI)",
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
        parser.add_argument("--cpu", help="Number of threads", default=1, type=int)

    def handle(
        self,
        file: str,
        organism: str,
        soterm: str,
        verbosity: int = 1,
        cpu: int = 1,
        **options
    ):
        """Execute the main function."""
        history_obj = History()
        history_obj.start(command="load_feature_publication", params=locals())
        if verbosity > 0:
            self.stdout.write("Preprocessing")

        try:
            FileValidator().validate(file)
            organism = retrieve_organism(organism)
        except ImportingError as e:
            history_obj.failure(description=str(e))
            raise CommandError(e)
        except IntegrityError as e:
            history_obj.failure(description=str(e))
            raise ImportingError(e)

        # retrieve only the file name
        filename = os.path.basename(file)

        try:
            feature_file = FeatureLoader(
                filename=filename, source="PUBLICATION", organism=organism
            )
        except ImportingError as e:
            history_obj.failure(description=str(e))
            raise CommandError(e)

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
            self.stdout.write("Loading feature publications")
        for task in tqdm(as_completed(tasks), total=len(tasks)):
            try:
                task.result()
            except ImportingError as e:
                history_obj.failure(description=str(e))
                raise CommandError(e)
        pool.shutdown()

        history_obj.success(description="Done")
        if verbosity > 0:
            self.stdout.write(self.style.SUCCESS("Done"))
