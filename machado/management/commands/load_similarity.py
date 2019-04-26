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
from tqdm import tqdm

from machado.loaders.common import FileValidator
from machado.loaders.exceptions import ImportingError
from machado.loaders.similarity import SimilarityLoader

VALID_FORMAT = ["blast-xml", "interproscan-xml"]


class Command(BaseCommand):
    """Load similarity file."""

    help = "Load similarity file"

    def add_arguments(self, parser):
        """Define the arguments."""
        parser.add_argument(
            "--file", help="Blast or InterproScan XML file", required=True, type=str
        )
        parser.add_argument(
            "--format", help="blast-xml or interproscan-xml", required=True, type=str
        )
        parser.add_argument(
            "--so_query",
            help="Query Sequence Ontology term. "
            "eg. assembly, mRNA, CDS, polypeptide",
            required=True,
            type=str,
        )
        parser.add_argument(
            "--so_subject",
            help="Subject Sequence Ontology "
            "term. eg. assembly, mRNA, CDS, polypeptide "
            "(protein_match if loading InterproScan or BLAST "
            "xml file)",
            required=True,
            type=str,
        )
        parser.add_argument(
            "--organism_query",
            help="Query's organism name. "
            "eg. 'Oryza sativa'. Cannot be multispecies'.",
            required=True,
            type=str,
        )
        parser.add_argument(
            "--organism_subject",
            help="Subject's organism "
            "name eg. 'Oryza sativa'. If using a multispecies "
            "database put 'multispecies multispecies'.",
            required=True,
            type=str,
        )
        parser.add_argument("--program", help="Program", required=True, type=str)
        parser.add_argument(
            "--programversion", help="Program version", required=True, type=str
        )
        parser.add_argument("--name", help="Name", required=False, type=str)
        parser.add_argument(
            "--description", help="Description", required=False, type=str
        )
        parser.add_argument("--algorithm", help="Algorithm", required=False, type=str)
        parser.add_argument("--cpu", help="Number of threads", default=1, type=int)

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
        **options
    ):
        """Execute the main function."""
        filename = os.path.basename(file)
        if organism_query == "mutispecies multispecies":
            raise CommandError("Query's organism cannot be multispecies")

        if format not in VALID_FORMAT:
            raise CommandError(
                "The format is not valid. Please choose: " "{}".format(VALID_FORMAT)
            )
        try:
            FileValidator().validate(file)
        except ImportingError as e:
            raise CommandError(e)

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
        except ImportingError as e:
            raise CommandError(e)

        try:
            similarity_records = SearchIO.parse(file, format)
        except ValueError as e:
            return CommandError(e)

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
            self.stdout.write("Loading")
        for task in tqdm(as_completed(tasks), total=len(tasks)):
            try:
                task.result()
            except ImportingError as e:
                raise CommandError(e)
        pool.shutdown()
        if verbosity > 0:
            self.stdout.write(self.style.SUCCESS("Done with {}".format(filename)))
