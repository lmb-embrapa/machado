# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Load RNA-seq expression data from LSTrAP output file exp_matrix.tpm.txt."""

import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError
from tqdm import tqdm

from machado.loaders.analysis import AnalysisLoader
from machado.loaders.common import FileValidator, FieldsValidator
from machado.loaders.exceptions import ImportingError


class Command(BaseCommand):
    """Load RNA-seq expression tpm data from LSTrAP exp_matrix.tpm.txt file."""

    help = """Load RNA-seq exp_matrix.tpm result file. This file is tabular
    and has SRR (SRA database) experiment IDs in columns and genes in lines.
    E.g.:

    gene    SRR5167848.htseq        SRR2302912.htseq    ...
    AT2G44195.1.TAIR10  0.0 0.6936967934559419  ...
    AT1G25375.1.TAIR10  2.369615950632963   10.7523002985671 ...
    ...

    The information about the features (genes) and assays (SRR experiments)
    need to be provided before, using 'python manage.py load_rnaseq_info'."""

    def add_arguments(self, parser):
        """Define the arguments."""
        parser.add_argument(
            "--file", help="tabular text file with gene counts", required=True, type=str
        )
        parser.add_argument(
            "--organism",
            help="Scientific name (e.g.: 'Oryza sativa')",
            required=True,
            type=str,
        )
        parser.add_argument(
            "--programversion",
            help="Version of the software (e.g.: '1.3')",
            required=True,
            type=str,
        )
        parser.add_argument("--name", help="Name", required=False, type=str)
        parser.add_argument(
            "--description", help="Description", required=False, type=str
        )
        parser.add_argument("--algorithm", help="Algorithm", required=False, type=str)
        parser.add_argument(
            "--assaydb",
            help="Assay database info (e.g.: 'SRA')",
            required=False,
            type=str,
        )
        parser.add_argument(
            "--timeexecuted",
            help="Time software was run. " "Mandatory format: e.g.: 'Oct-16-2016'",
            required=False,
            type=str,
        )
        parser.add_argument(
            "--program",
            help="Name of the software (e.g.: 'LSTrAP')",
            default="LSTrAP",
            type=str,
        )
        parser.add_argument(
            "--norm",
            help="Normalized data: 1-yes (tpm, fpkm, etc.); "
            "0-no (raw counts); default is 1)",
            default=1,
            type=int,
        )
        parser.add_argument("--cpu", help="Number of threads", default=1, type=int)

    def handle(
        self,
        file: str,
        organism: str,
        program: str,
        programversion: str,
        name: str = None,
        description: str = None,
        algorithm: str = None,
        assaydb: str = "SRA",
        timeexecuted: str = None,
        norm: int = 1,
        cpu: int = 1,
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

        # start reading file
        try:
            rnaseq_data = open(file, "r")
            # retrieve only the file name
        except ImportingError as e:
            raise CommandError(e)
        header = 1
        # analysis_list = defaultdict(list)
        analysis_list = list()
        # instantiate Loader
        analysis_file = AnalysisLoader()
        pool = ThreadPoolExecutor(max_workers=cpu)
        tasks = list()
        for line in rnaseq_data:
            fields = re.split("\t", line.rstrip())
            nfields = len(fields)
            # validate fields within line
            try:
                FieldsValidator().validate(nfields, fields)
            except ImportingError as e:
                raise CommandError(e)
                # read header and instantiate analysis object for each assay
                # e.g. SRR12345.
            if header:
                # first element is the string "gene" - need to be removed
                fields.pop(0)
                for i in range(len(fields)):
                    # parse field to get SRA ID. e.g.: SRR5167848.htseq
                    # try to remove ".htseq" part of string
                    string = re.match(r"(\w+)\.(\w+)", fields[i])
                    try:
                        assay = string.group(1)
                    except IntegrityError as e:
                        raise CommandError(e)
                    # store analysis
                    try:
                        analysis = analysis_file.store_analysis(
                            program=program,
                            sourcename=fields[i],
                            programversion=programversion,
                            timeexecuted=timeexecuted,
                            algorithm=algorithm,
                            name=assay,
                            description=description,
                            filename=filename,
                        )
                    except ImportingError as e:
                        raise CommandError(e)
                    # store quantification
                    try:
                        analysis_file.store_quantification(
                            analysis=analysis, assayacc=assay
                        )
                    except ImportingError as e:
                        raise CommandError(e)
                    # finally, store each analysis in a list.
                    analysis_list.insert(i, analysis)
                header = 0
            else:
                # first element is the feature acc. "e.g.: AT2G44195.1.TAIR10"
                feature_name = fields.pop(0)
                for i in range(len(fields)):
                    if norm:
                        normscore = fields[i]
                        rawscore = None
                    else:
                        normscore = None
                        rawscore = fields[i]
                    # store analysis feature for each value
                    tasks.append(
                        pool.submit(
                            analysis_file.store_analysisfeature,
                            analysis_list[i],
                            feature_name,
                            organism,
                            rawscore,
                            normscore,
                        )
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
