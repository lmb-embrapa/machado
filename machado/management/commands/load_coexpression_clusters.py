# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Load clusters of coexpression data from LSTRAP outfile mcl.clusters.txt."""

import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError
from tqdm import tqdm

from machado.loaders.common import FileValidator, FieldsValidator
from machado.loaders.common import get_num_lines
from machado.loaders.common import retrieve_organism
from machado.loaders.exceptions import ImportingError
from machado.loaders.feature import FeatureLoader
from machado.models import Cv, Cvterm, Dbxref, Db


class Command(BaseCommand):
    """Load LSTRAP output file mcl.clusters.txt results."""

    help = """Load 'mcl.clusters.txt' output result file from LSTrAP.
The 'mcl.clusters.txt' is a tab separated, headless file and have the format
as follows (each line is a cluster):
ath_coexpr_mcl_1:    AT3G18715.1.TAIR10	AT3G08790.1.TAIR10  AT5G42230.1.TAIR10
ath_coexpr_mcl_2:    AT1G27040.1.TAIR10	AT1G71692.1.TAIR10
ath_coexpr_mcl_3:    AT5G24750.1.TAIR10
...
and so on.
The features need to be loaded previously or won't be registered."""

    def add_arguments(self, parser):
        """Define the arguments."""
        parser.add_argument(
            "--file", help="'mcl.clusters.txt' File", required=True, type=str
        )
        parser.add_argument(
            "--soterm",
            help="sequence ontology term 'e.g. mRNA'",
            required=False,
            default="mRNA",
            type=str,
        )
        parser.add_argument(
            "--organism",
            help="Scientific name (e.g.: 'Oryza sativa')",
            required=True,
            type=str,
        )
        parser.add_argument("--cpu", help="Number of threads", default=1, type=int)

    def handle(
        self,
        file: str,
        organism: str,
        soterm: str = "mRNA",
        cpu: int = 1,
        verbosity: int = 0,
        **options
    ):
        """Execute the main function."""
        filename = os.path.basename(file)
        if verbosity > 0:
            self.stdout.write("Processing file: {}".format(filename))

        try:
            organism = retrieve_organism(organism)
        except IntegrityError as e:
            raise ImportingError(e)
        try:
            FileValidator().validate(file)
        except ImportingError as e:
            raise CommandError(e)
        try:
            clusters = open(file, "r")
            # retrieve only the file name
        except ImportingError as e:
            raise CommandError(e)

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
        featureloader = FeatureLoader(source=source, filename=filename)

        pool = ThreadPoolExecutor(max_workers=cpu)
        # each line is an coexpression cluster group
        for line in tqdm(clusters, total=get_num_lines(file)):
            name = ""
            fields = re.split(r"\s+", line.strip())
            nfields = len(fields)
            try:
                FieldsValidator().validate(nfields, fields)
            except ImportingError as e:
                raise CommandError(e)

            if re.search(r"^(\w+)\:", fields[0]):
                group_field = re.match(r"^(\w+)\:", fields[0])
                name = group_field.group(1)
            else:
                raise CommandError("Cluster identification has problems.")
            # remove cluster name before loading
            fields.pop(0)
            # get cvterm for correlation
            tasks.append(
                pool.submit(
                    featureloader.store_feature_groups,
                    group=fields,
                    soterm=soterm,
                    term=cvterm_cluster.cvterm_id,
                    value=name,
                )
            )
        if verbosity > 0:
            self.stdout.write("Loading")
        for task in tqdm(as_completed(tasks), total=len(tasks)):
            if task.result():
                raise (task.result())
        pool.shutdown()
        if verbosity > 0:
            self.stdout.write(self.style.SUCCESS("Done with {}".format(filename)))
