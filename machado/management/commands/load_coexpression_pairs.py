# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Load coexpression data from LSTRAP output file pcc.mcl.txt."""

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
    """Load LSTRAP output file pcc.mcl.txt results."""

    help = """Load 'pcc.mcl.txt' output result file from LSTrAP.
The 'pcc.mcl.txt' file is headless and have the format as follows:
AT2G44195.1.TAIR10	AT1G30080.1.TAIR10	0.18189286870895194
AT2G44195.1.TAIR10	AT5G24750.1.TAIR10	0.1715779378273995
...
and so on.
The value of the third column is a Pearson correlation coefficient subtracted
from 0.7 (PCC - 0.7). To obtain the original PCC value, it must be added 0.7 to
every value of the third column.
The feature pairs from columns 1 and 2 need to be loaded previously."""

    def add_arguments(self, parser):
        """Define the arguments."""
        parser.add_argument("--filename",
                            help="'pcc.mcl.txt' File",
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
            pairs = open(filename, 'r')
            # retrieve only the file name
        except ImportingError as e:
            raise CommandError(e)

        pool = ThreadPoolExecutor(max_workers=cpu)
        tasks = list()
        # each line is an orthologous group
        for line in pairs:
            # a pair of features plus the PCC value
            nfields = 3
            fields = re.split(r'\s+', line.rstrip())
            try:
                FieldsValidator().validate(nfields, fields)
            except ImportingError as e:
                raise CommandError(e)
            # get corrected PCC value (last item from fields list)
            value = float(fields.pop()) + 0.7
            pair = CoexpressionLoader(
                    value=str(value),
                    filename=filename,
                    organism=organism)
            tasks.append(pool.submit(
                       pair.store_coexpression_pairs, fields))
        if verbosity > 0:
            self.stdout.write('Loading')
        for task in tqdm(as_completed(tasks), total=len(tasks)):
            if task.result():
                raise(task.result())
        self.stdout.write(self.style.SUCCESS('Done'))
