# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Load coexpression data from LSTRAP output file pcc.mcl.txt."""

import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

from django.core.management.base import BaseCommand, CommandError
from tqdm import tqdm

from machado.loaders.common import FileValidator, FieldsValidator
from machado.loaders.common import get_num_lines
from machado.loaders.exceptions import ImportingError
from machado.loaders.feature import FeatureLoader
from machado.models import Cvterm


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
        parser.add_argument(
            "--file", help="'pcc.mcl.txt' File", required=True, type=str
        )
        parser.add_argument(
            "--soterm",
            help="sequence ontology term 'e.g. mRNA'",
            required=False,
            default="mRNA",
            type=str,
        )
        parser.add_argument("--cpu", help="Number of threads", default=1, type=int)

    def handle(
        self,
        file: str,
        cpu: int = 1,
        soterm: str = "mRNA",
        verbosity: int = 0,
        **options
    ):
        """Execute the main function."""
        filename = os.path.basename(file)
        if verbosity > 0:
            self.stdout.write("Processing file: {}".format(filename))

        try:
            FileValidator().validate(file)
        except ImportingError as e:
            raise CommandError(e)
        try:
            pairs = open(file, "r")
            # retrieve only the file name
        except ImportingError as e:
            raise CommandError(e)

        cvterm_corel = Cvterm.objects.get(
            name="correlated with", cv__name="relationship"
        ).cvterm_id
        # feature source is not needed here
        source = "null"
        featureloader = FeatureLoader(source=source, filename=filename)
        size = get_num_lines(file)
        # every cpu should be able to handle 5 tasks
        chunk = cpu * 5
        with ThreadPoolExecutor(max_workers=cpu) as pool:
            tasks = list()
            for line in tqdm(pairs, total=size):
                nfields = 3
                fields = re.split(r"\s+", line.rstrip())
                try:
                    FieldsValidator().validate(nfields, fields)
                except ImportingError as e:
                    raise CommandError(e)
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
            self.stdout.write(self.style.SUCCESS("Done with {}".format(filename)))
