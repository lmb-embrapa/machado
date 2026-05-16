# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

from machado.models import Cv, Db, Dbxref, Cvterm

"""Load clusters of coexpression data from LSTRAP outfile mcl.clusters.txt."""

import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

from django.core.management.base import BaseCommand, CommandError
from machado.management.commands._base import HistoryCommandMixin
from django.db.utils import IntegrityError
from tqdm import tqdm

from machado.loaders.common import FileValidator, FieldsValidator
from machado.loaders.common import get_num_lines
from machado.loaders.common import retrieve_organism
from machado.loaders.exceptions import ImportingError
from machado.loaders.feature import FeatureLoader


class Command(HistoryCommandMixin, BaseCommand):
    """Load LSTRAP output file mcl.clusters.txt results."""

    help = "Load LSTrAP 'mcl.clusters.txt' coexpression clusters output file" ""

    def add_arguments(self, parser):
        """Define the arguments."""
        parser.add_argument(
            "--file",
            help="Path to the 'mcl.clusters.txt' file",
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
            "--organism",
            help="Scientific name of the species (e.g., 'Oryza sativa')",
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
        organism: str,
        soterm: str = "mRNA",
        cpu: int = 1,
        verbosity: int = 0,
        **options,
    ):
        """Execute the main function."""
        filename = os.path.basename(file)
        if verbosity > 0:
            self.stdout.write("Processing file: {}".format(filename))

        try:
            organism = retrieve_organism(organism)
        except IntegrityError as e:
            raise ImportingError(e)

        FileValidator().validate(file)
        try:
            # retrieve only the file name
            clusters = open(file, "r")
        except IntegrityError as e:
            raise ImportingError(e)

        tasks = list()
        cv, created = Cv.objects.get_or_create(name="feature_property")
        coexp_db, created = Db.objects.get_or_create(name="LSTRAP_SOURCE")
        coexp_dbxref, created = Dbxref.objects.get_or_create(
            accession="LSTRAP_SOURCE", db=coexp_db
        )
        cvterm_cluster, created = Cvterm.objects.get_or_create(
            name="coexpression group",
            cv=cv,
            dbxref=coexp_dbxref,
            is_obsolete=0,
            is_relationshiptype=0,
        )
        # feature source is not needed here
        source = "null"
        featureloader = FeatureLoader(
            source=source, filename=filename, organism=organism
        )

        pool = ThreadPoolExecutor(max_workers=cpu)
        # each line is an coexpression cluster group
        for line in tqdm(clusters, total=get_num_lines(file), disable=verbosity == 0):
            name = ""
            fields = re.split(r"\s+", line.strip())
            nfields = len(fields)
            FieldsValidator().validate(nfields, fields)
            if re.search(r"^(\w+)\:", fields[0]):
                group_field = re.match(r"^(\w+)\:", fields[0])
                name = group_field.group(1)
            else:
                raise CommandError("Invalid cluster identification format in file.")
            # remove cluster name before loading
            fields.pop(0)
            # get cvterm for correlation
            tasks.append(
                pool.submit(
                    featureloader.store_feature_groups,
                    group=fields,
                    organism=organism,
                    soterm=soterm,
                    term=cvterm_cluster.cvterm_id,
                    value=name,
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
