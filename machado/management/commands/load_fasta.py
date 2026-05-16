# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Load FASTA file."""

import os
from concurrent.futures import ThreadPoolExecutor, as_completed

from Bio import SeqIO
from django.core.management.base import BaseCommand
from machado.management.commands._base import HistoryCommandMixin
from tqdm import tqdm

from machado.loaders.common import FileValidator, retrieve_organism
from machado.loaders.sequence import SequenceLoader


class Command(HistoryCommandMixin, BaseCommand):
    """Load FASTA file."""

    help = "Load sequences from a FASTA file into the database"

    def add_arguments(self, parser):
        """Define the arguments."""
        parser.add_argument(
            "--file", help="Path to the FASTA file", required=True, type=str
        )
        parser.add_argument(
            "--organism",
            help="Scientific name of the species (e.g., Homo sapiens)",
            required=True,
            type=str,
        )
        parser.add_argument(
            "--soterm",
            help="Sequence Ontology (SO) term (e.g., 'chromosome', 'assembly')",
            required=True,
            type=str,
        )
        parser.add_argument(
            "--nosequence",
            help="Register the feature name only, skipping sequence residue loading",
            required=False,
            action="store_true",
        )
        parser.add_argument(
            "--cpu",
            help="Number of threads for parallel processing",
            default=1,
            type=int,
        )
        parser.add_argument(
            "--description",
            help="Source description for the FASTA source",
            required=False,
            type=str,
        )
        parser.add_argument(
            "--url", help="URL of the sequence source", required=False, type=str
        )
        parser.add_argument(
            "--doi",
            help="DOI of the article reference to "
            "this sequence. E.g.: 10.1111/s12122-012-1313-4",
            required=False,
            type=str,
        )

    def handle(
        self,
        file: str,
        organism: str,
        soterm: str,
        nosequence: bool = False,
        cpu: int = 1,
        description: str = None,
        url: str = None,
        doi: str = None,
        verbosity: int = 1,
        **options,
    ) -> None:
        """Execute the main function."""

        if verbosity > 0:
            self.stdout.write("Preprocessing data...")

        FileValidator().validate(file)
        organism = retrieve_organism(organism)
        # retrieve only the file name
        filename = os.path.basename(file)
        sequence_file = SequenceLoader(
            filename=filename,
            organism=organism,
            description=description,
            url=url,
            doi=doi,
        )
        fasta_sequences = SeqIO.parse(open(file), "fasta")

        pool = ThreadPoolExecutor(max_workers=cpu)
        tasks = list()
        for fasta in fasta_sequences:
            tasks.append(
                pool.submit(
                    sequence_file.store_biopython_seq_record, fasta, soterm, nosequence
                )
            )
        if verbosity > 0:
            self.stdout.write("Loading data...")
        for task in tqdm(as_completed(tasks), total=len(tasks), disable=verbosity == 0):
            if task.result():
                raise (task.result())
        pool.shutdown()

        if verbosity > 0:
            self.stdout.write(
                self.style.SUCCESS("Successfully processed {}".format(filename))
            )
