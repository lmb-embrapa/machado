# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Load GFF file."""

import os
from concurrent.futures import ThreadPoolExecutor, as_completed

import pysam
from django.core.management.base import BaseCommand
from machado.management.commands._base import HistoryCommandMixin
from tqdm import tqdm

from machado.loaders.common import FileValidator, get_num_lines, retrieve_organism
from machado.loaders.exceptions import ImportingError
from machado.loaders.feature import FeatureLoader


class Command(HistoryCommandMixin, BaseCommand):
    """Load GFF file."""

    help = "Load genomic features from a GFF3 file (Tabix-indexed)"

    def add_arguments(self, parser):
        """Define the arguments."""
        parser.add_argument(
            "--file",
            help="Path to the GFF3 genome file indexed with tabix "
            "(see http://www.htslib.org/doc/tabix.html)",
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
            "--ignore",
            help="List of feature types to ignore (e.g., chromosome, scaffold)",
            required=False,
            nargs="+",
            type=str,
        )
        parser.add_argument(
            "--qtl",
            help="Set this flag to handle GFF files from QTLDB",
            action="store_true",
        )
        parser.add_argument(
            "--doi",
            help="DOI of the article reference to "
            "this sequence. E.g.: 10.1111/s12122-012-1313-4",
            required=False,
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
        doi: str = None,
        ignore: str = None,
        qtl: bool = False,
        cpu: int = 1,
        verbosity: int = 1,
        **options,
    ):
        """Execute the main function."""
        # retrieve only the file name
        filename = os.path.basename(file)
        if verbosity > 0:
            self.stdout.write("Processing file: {}".format(filename))

        FileValidator().validate(file)
        organism = retrieve_organism(organism)

        try:
            index_file = "{}.tbi".format(file)
            FileValidator().validate(index_file)
        except ImportingError:
            try:
                index_file = "{}.csi".format(file)
                FileValidator().validate(index_file)
            except ImportingError:
                raise ImportingError(
                    "Required Tabix index file (.tbi or .csi) not found.", file=file
                )
        feature_file = FeatureLoader(
            filename=filename, source="GFF_SOURCE", organism=organism, doi=doi
        )
        pool = ThreadPoolExecutor(max_workers=cpu)
        tasks = list()

        chunk_size = cpu * 2

        # Load the GFF3 file
        with open(file) as tbx_file:
            tbx = pysam.TabixFile(filename=tbx_file.name, index=index_file)
            for i, row in tqdm(
                enumerate(tbx.fetch(parser=pysam.asGTF())), total=get_num_lines(file)
            , disable=verbosity == 0):
                if ignore is not None and row.feature in ignore:
                    continue
                tasks.append(
                    pool.submit(
                        feature_file.store_tabix_GFF_feature, row, qtl, line=i + 1
                    )
                )

                if len(tasks) >= chunk_size:
                    for task in as_completed(tasks):
                        task.result()
                    tasks.clear()
            else:
                for task in as_completed(tasks):
                    task.result()
                tasks.clear()

        pool.shutdown()

        if verbosity > 0:
            self.stdout.write("Loading relationships...")

        pool = ThreadPoolExecutor(max_workers=cpu)
        tasks = list()

        for item in feature_file.relationships:
            tasks.append(
                pool.submit(
                    feature_file.store_relationship,
                    item["subject_id"],
                    item["object_id"],
                )
            )

        for task in tqdm(as_completed(tasks), total=len(tasks), disable=verbosity == 0):
            task.result()
        pool.shutdown()

        if feature_file.ignored_attrs is not None:
            self.stdout.write(
                self.style.WARNING(
                    "Ignored attributes: {}".format(feature_file.ignored_attrs)
                )
            )

        if verbosity > 0:
            self.stdout.write(
                self.style.SUCCESS("Successfully processed {}".format(filename))
            )
