# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Load clusters of coexpression data from LSTRAP outfile mcl.clusters.txt."""

from machado.loaders.common import FileValidator, FieldsValidator
from machado.loaders.coexpression import CoexpressionLoader
from machado.loaders.exceptions import ImportingError
from django.db.utils import IntegrityError
from machado.loaders.common import retrieve_organism
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.core.management.base import BaseCommand, CommandError
from tqdm import tqdm
import re


class Command(BaseCommand):
    """Load LSTRAP output file mcl.clusters.txt results."""

    help = """Load 'mcl.clusters.txt' output result file from LSTrAP.
The 'mcl.clusters.txt' is a tab separated, headless file and have the format
as follows (each line is a cluster):
AT3G18715.1.TAIR10	AT3G08790.1.TAIR10	AT5G42230.1.TAIR10
AT1G27040.1.TAIR10	AT1G71692.1.TAIR10
AT5G24750.1.TAIR10
...
and so on.
The features need to be loaded previously or won't be registered."""

    def add_arguments(self, parser):
        """Define the arguments."""
        parser.add_argument("--filename",
                            help="'mcl.clusters.txt' File",
                            required=True,
                            type=str)
        parser.add_argument("--organism",
                            help="Scientific name (e.g.: 'Oryza sativa')",
                            required=True,
                            type=str)
        parser.add_argument("--cpu",
                            help="Number of threads",
                            default=1,
                            type=int)

    def handle(self,
               filename: str,
               organism: str,
               cpu: int = 1,
               verbosity: int = 0,
               **options):
        """Execute the main function."""
        if verbosity > 0:
            self.stdout.write('Preprocessing')

        try:
            organism = retrieve_organism(organism)
        except IntegrityError as e:
            raise ImportingError(e)
        try:
            FileValidator().validate(filename)
        except ImportingError as e:
            raise CommandError(e)
        try:
            clusters = open(filename, 'r')
            # retrieve only the file name
        except ImportingError as e:
            raise CommandError(e)

        pool = ThreadPoolExecutor(max_workers=cpu)
        tasks = list()
        # arbitrary naming...
        value = "MCL_CLUSTER"
        # each line is an orthologous group
        for line in clusters:
            # a pair of features plus the PCC value
            fields = re.split(r'\s+', line.rstrip())
            nfields = len(fields)

            try:
                FieldsValidator().validate(nfields, fields)
            except ImportingError as e:
                raise CommandError(e)
            cluster = CoexpressionLoader(value=value,
                                         filename=filename,
                                         organism=organism)
            tasks.append(pool.submit(
                       cluster.store_coexpression_clusters, fields))
        if verbosity > 0:
            self.stdout.write('Loading')
        for task in tqdm(as_completed(tasks), total=len(tasks)):
            if task.result():
                raise(task.result())
        self.stdout.write(self.style.SUCCESS('Done'))
