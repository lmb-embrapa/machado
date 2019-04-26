# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Load GFF file."""

import os
from concurrent.futures import ThreadPoolExecutor, as_completed

import pysam
from django.core.management.base import BaseCommand, CommandError
from tqdm import tqdm

from machado.loaders.common import FileValidator, get_num_lines
from machado.loaders.exceptions import ImportingError
from machado.loaders.feature import FeatureLoader


class Command(BaseCommand):
    """Load GFF file."""

    help = "Load GFF3 file indexed with tabix."

    def add_arguments(self, parser):
        """Define the arguments."""
        parser.add_argument(
            "--file",
            help="GFF3 genome file indexed with tabix"
            "(see http://www.htslib.org/doc/tabix.html)",
            required=True,
            type=str,
        )
        parser.add_argument(
            "--organism",
            help="Species name (eg. Homo " "sapiens, Mus musculus)",
            required=True,
            type=str,
        )
        parser.add_argument(
            "--ignore",
            help="List of feature " "types to ignore (eg. chromosome,scaffold)",
            required=False,
            nargs="+",
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

    def handle(
        self,
        file: str,
        organism: str,
        doi: str = None,
        ignore: str = None,
        cpu: int = 1,
        verbosity: int = 1,
        **options
    ):
        """Execute the main function."""
        # retrieve only the file name
        filename = os.path.basename(file)
        if verbosity > 0:
            self.stdout.write("Processing file: {}".format(filename))

        try:
            FileValidator().validate(file)
        except ImportingError as e:
            raise CommandError(e)

        try:
            index_file = "{}.tbi".format(file)
            FileValidator().validate(index_file)
        except ImportingError as e:
            try:
                index_file = "{}.csi".format(file)
                FileValidator().validate(index_file)
            except ImportingError as e:
                raise CommandError("No index found (.tbi/.csi).".format(e))

        try:
            feature_file = FeatureLoader(
                filename=filename, source="GFF_source", doi=doi
            )
        except ImportingError as e:
            raise CommandError(e)

        pool = ThreadPoolExecutor(max_workers=cpu)
        tasks = list()

        chunk_size = cpu * 2

        # Load the GFF3 file
        with open(file) as tbx_file:
            tbx = pysam.TabixFile(filename=tbx_file.name, index=index_file)
            for row in tqdm(tbx.fetch(parser=pysam.asGTF()), total=get_num_lines(file)):
                if ignore is not None and row.feature in ignore:
                    continue
                tasks.append(
                    pool.submit(feature_file.store_tabix_feature, row, organism)
                )

                if len(tasks) >= chunk_size:
                    for task in as_completed(tasks):
                        try:
                            task.result()
                        except ImportingError as e:
                            raise CommandError(e)
                    tasks.clear()
            else:
                for task in as_completed(tasks):
                    try:
                        task.result()
                    except ImportingError as e:
                        raise CommandError(e)
                tasks.clear()

        pool.shutdown()

        if verbosity > 0:
            self.stdout.write("Loading relationships")

        feature_file.store_relationships(organism=organism)

        if feature_file.ignored_attrs is not None:
            self.stdout.write(
                self.style.WARNING(
                    "Ignored attrs: {}".format(feature_file.ignored_attrs)
                )
            )

        if verbosity > 0:
            self.stdout.write(self.style.SUCCESS("Done with {}".format(filename)))
