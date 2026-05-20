# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Load feature sequence file."""

import os
from concurrent.futures import ThreadPoolExecutor, as_completed

from Bio import SeqIO
from django.core.management.base import BaseCommand
from machado.management.commands._base import HistoryCommandMixin
from tqdm import tqdm

from machado.loaders.common import FileValidator, retrieve_organism
from machado.loaders.sequence import SequenceLoader


class Command(HistoryCommandMixin, BaseCommand):
    """Load feature sequence file."""

    help = "Load FASTA file and add sequences to existing features"

    def add_arguments(self, parser):
        """Define the arguments."""
        parser.add_argument(
            "--file", help="Path to the FASTA file", required=True, type=str
        )
        parser.add_argument(
            "--soterm",
            help="Sequence Ontology (SO) term (e.g., 'mRNA', 'polypeptide')",
            required=True,
            type=str,
        )
        parser.add_argument(
            "--organism",
            help="Scientific name of the species (e.g., 'Homo sapiens')",
            required=True,
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
        soterm: str,
        organism: str,
        verbosity: int = 1,
        cpu: int = 1,
        **options,
    ):
        """Execute the main function."""
        FileValidator().validate(file)
        organism = retrieve_organism(organism)
        # retrieve only the file name
        filename = os.path.basename(file)
        sequence_file = SequenceLoader(filename=filename, organism=organism)
        if verbosity > 0:
            self.stdout.write("Processing file: {}".format(filename))

        fasta_sequences = SeqIO.parse(open(file), "fasta")
        pool = ThreadPoolExecutor(max_workers=cpu)
        tasks = list()
        for fasta in fasta_sequences:
            tasks.append(
                pool.submit(sequence_file.add_sequence_to_feature, fasta, soterm)
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
                self.style.SUCCESS("Successfully processed {}".format(filename))
            )
