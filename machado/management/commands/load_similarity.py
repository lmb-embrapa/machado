# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Load similarity file."""

import os
from concurrent.futures import ThreadPoolExecutor, as_completed

from Bio import SearchIO
from django.core.management.base import BaseCommand, CommandError
from machado.management.commands._base import HistoryCommandMixin
from tqdm import tqdm

from machado.loaders.common import FileValidator
from machado.loaders.similarity import SimilarityLoader

VALID_FORMAT = ["blast-xml", "interproscan-xml"]


class Command(HistoryCommandMixin, BaseCommand):
    """Load similarity file."""

    help = "Load similarity search results (BLAST/InterproScan) into the database"

    def add_arguments(self, parser):
        """Define the arguments."""
        parser.add_argument(
            "--file",
            help="Path to the Blast or InterproScan XML file",
            required=True,
            type=str,
        )
        parser.add_argument(
            "--format", help="blast-xml or interproscan-xml", required=True, type=str
        )
        parser.add_argument(
            "--so_query",
            help="Sequence Ontology (SO) term for the query (e.g., mRNA, polypeptide)",
            required=True,
            type=str,
        )
        parser.add_argument(
            "--so_subject",
            help="Sequence Ontology (SO) term for the subject (e.g., polypeptide, protein_match)",
            required=True,
            type=str,
        )
        parser.add_argument(
            "--organism_query",
            help="Scientific name of the query organism (e.g., 'Oryza sativa')",
            required=True,
            type=str,
        )
        parser.add_argument(
            "--organism_subject",
            help="Scientific name of the subject organism (use 'multispecies multispecies' for databases)",
            required=True,
            type=str,
        )
        parser.add_argument("--program", help="Program", required=True, type=str)
        parser.add_argument(
            "--programversion",
            help="Version of the program used",
            required=True,
            type=str,
        )
        parser.add_argument("--name", help="Name", required=False, type=str)
        parser.add_argument(
            "--description", help="Description", required=False, type=str
        )
        parser.add_argument("--algorithm", help="Algorithm", required=False, type=str)
        parser.add_argument(
            "--cpu",
            help="Number of threads for parallel processing",
            default=1,
            type=int,
        )

    def handle(
        self,
        file: str,
        format: str,
        so_query: str,
        so_subject: str,
        organism_query: str,
        organism_subject: str,
        program: str,
        programversion: str,
        name: str = None,
        description: str = None,
        algorithm: str = None,
        cpu: int = 1,
        verbosity: int = 1,
        **options,
    ):
        """Execute the main function."""
        filename = os.path.basename(file)
        if organism_query == "mutispecies multispecies":
            raise CommandError("Query organism cannot be 'multispecies'.")

        if format not in VALID_FORMAT:
            raise CommandError(
                "Invalid format. Please specify one of: {}".format(
                    ", ".join(VALID_FORMAT)
                )
            )
        FileValidator().validate(file)
        try:
            similarity_file = SimilarityLoader(
                filename=filename,
                so_query=so_query,
                so_subject=so_subject,
                org_query=organism_query,
                org_subject=organism_subject,
                algorithm=algorithm,
                name=name,
                description=description,
                program=program,
                programversion=programversion,
                input_format=format,
            )
            similarity_records = SearchIO.parse(file, format)
        except ValueError as e:
            raise CommandError(e)

        pool = ThreadPoolExecutor(max_workers=cpu)
        tasks = list()
        if verbosity > 0:
            self.stdout.write("Processing file: {}".format(filename))
        for record in similarity_records:
            if len(record.hsps) > 0:
                tasks.append(
                    pool.submit(similarity_file.store_bio_searchio_query_result, record)
                )
        if verbosity > 0:
            self.stdout.write("Loading data...")
        for task in tqdm(as_completed(tasks), total=len(tasks), disable=verbosity == 0):
            task.result()
        pool.shutdown()

        if verbosity > 0:
            self.stdout.write(
                self.style.SUCCESS("Successfully processed {}".format(filename))
            )
