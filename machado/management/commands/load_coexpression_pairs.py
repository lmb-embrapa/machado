# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

from machado.models import Cvterm

"""Load coexpression data from LSTRAP output file pcc.mcl.txt."""

import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

from django.core.management.base import BaseCommand
from machado.management.commands._base import HistoryCommandMixin
from tqdm import tqdm

from machado.loaders.common import FileValidator, FieldsValidator, retrieve_organism
from machado.loaders.common import get_num_lines
from machado.loaders.feature import FeatureLoader


class Command(HistoryCommandMixin, BaseCommand):
    """Load LSTRAP output file pcc.mcl.txt results."""

    help = "Load LSTrAP 'pcc.mcl.txt' coexpression pairs output file" ""

    def add_arguments(self, parser):
        """Define the arguments."""
        parser.add_argument(
            "--file", help="Path to the 'pcc.mcl.txt' file", required=True, type=str
        )
        parser.add_argument(
            "--organism",
            help="Scientific name of the species (e.g., 'Oryza sativa')",
            required=True,
            type=str,
        )
        parser.add_argument(
            "--soterm",
            help="Sequence Ontology (SO) term (e.g., 'mRNA')",
            required=False,
            default="mRNA",
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
        cpu: int = 1,
        soterm: str = "mRNA",
        verbosity: int = 0,
        **options,
    ):
        """Execute the main function."""
        filename = os.path.basename(file)
        if verbosity > 0:
            self.stdout.write("Processing file: {}".format(filename))

        FileValidator().validate(file)
        organism = retrieve_organism(organism)
        pairs = open(file, "r")
        # retrieve only the file name

        cvterm_corel = Cvterm.objects.get(
            name="correlated with", cv__name="relationship"
        ).cvterm_id
        # feature source is not needed here
        source = "null"
        featureloader = FeatureLoader(
            source=source, filename=filename, organism=organism
        )
        size = get_num_lines(file)
        # every cpu should be able to handle 5 tasks
        chunk = cpu * 5
        with ThreadPoolExecutor(max_workers=cpu) as pool:
            tasks = list()
            for line in tqdm(pairs, total=size, disable=verbosity == 0):
                nfields = 3
                fields = re.split(r"\s+", line.rstrip())
                FieldsValidator().validate(nfields, fields)
                # get corrected PCC value (last item from fields list)
                value = float(fields.pop()) + 0.7
                tasks.append(
                    pool.submit(
                        featureloader.store_feature_pairs,
                        pair=fields,
                        soterm=soterm,
                        term=cvterm_corel,
                        value=value,
                    )
                )
                if len(tasks) >= chunk:
                    for task in as_completed(tasks):
                        if task.result():
                            raise (task.result())
                    tasks.clear()
            else:
                for task in as_completed(tasks):
                    if task.result():
                        raise (task.result())
                tasks.clear()
            pool.shutdown()
        if verbosity > 0:
            self.stdout.write(
                self.style.SUCCESS("Successfully processed {}".format(filename))
            )
