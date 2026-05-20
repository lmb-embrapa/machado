# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Load RNA-seq expression data from LSTrAP output file exp_matrix.tpm.txt."""

import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError
from machado.management.commands._base import HistoryCommandMixin
from tqdm import tqdm

from machado.loaders.analysis import AnalysisLoader
from machado.loaders.common import FileValidator, FieldsValidator
from machado.loaders.exceptions import ImportingError


class Command(HistoryCommandMixin, BaseCommand):
    """Load RNA-seq expression tpm data from LSTrAP exp_matrix.tpm.txt file."""

    help = "Load RNA-seq expression data (TPM/counts) from a tab-separated file"

    def add_arguments(self, parser):
        """Define the arguments."""
        parser.add_argument(
            "--file",
            help="Path to the tabular text file containing gene counts",
            required=True,
            type=str,
        )
        parser.add_argument(
            "--organism",
            help="Scientific name of the species (e.g., 'Oryza sativa')",
            required=True,
            type=str,
        )
        parser.add_argument(
            "--programversion",
            help="Software version (e.g., '1.3')",
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
            help="Database name for assay information (e.g., 'SRA')",
            required=False,
            type=str,
        )
        parser.add_argument(
            "--timeexecuted",
            help="Execution date (format: 'Oct-16-2016')",
            required=False,
            type=str,
        )
        parser.add_argument(
            "--program",
            help="Name of the software (e.g., 'LSTrAP')",
            default="LSTrAP",
            type=str,
        )
        parser.add_argument(
            "--norm",
            help="Data normalization: 1 for yes (TPM, FPKM, etc.), 0 for no (raw counts)",
            default=1,
            type=int,
        )
        parser.add_argument(
            "--ignorenotfound",
            help="Continue processing if a feature is not found",
            required=False,
            action="store_true",
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
        ignorenotfound: bool = False,
        **options,
    ):
        """Execute the main function."""
        filename = os.path.basename(file)
        if verbosity > 0:
            self.stdout.write("Processing file: {}".format(filename))
        FileValidator().validate(file)
        # start reading file
        rnaseq_data = open(file, "r")
        # retrieve only the file name
        header = 1
        # analysis_list = defaultdict(list)
        analysis_list = list()
        # instantiate Loader
        analysis_file = AnalysisLoader()
        pool = ThreadPoolExecutor(max_workers=cpu)
        tasks = list()
        not_found = list()
        for line in rnaseq_data:
            fields = re.split("\t", line.rstrip())
            nfields = len(fields)
            # validate fields within line
            FieldsValidator().validate(nfields, fields)
            if header:
                # first element is the string "gene" - need to be removed
                fields.pop(0)
                for i in range(len(fields)):
                    # parse field to get SRA ID. e.g.: SRR5167848.htseq
                    # try to remove ".htseq" part of string
                    string = re.match(r"(\w+)\.(\w+)", fields[i])
                    assay = string.group(1)
                    # store analysis
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
                    # store quantification
                    analysis_file.store_quantification(
                        analysis=analysis, assayacc=assay, assaydb=assaydb
                    )
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
            self.stdout.write("Loading data...")

        for task in tqdm(as_completed(tasks), total=len(tasks), disable=verbosity == 0):
            try:
                task.result()
            except ObjectDoesNotExist as e:
                not_found.append(e)
                if not ignorenotfound:
                    raise CommandError(e)
            except ImportingError as e:
                raise CommandError(e)
        pool.shutdown()

        if verbosity > 0:
            self.stdout.write("List of features not found:")
            for item in not_found:
                self.stdout.write("- {}\n".format(item))

        if verbosity > 0:
            self.stdout.write(
                self.style.SUCCESS("Successfully processed {}".format(filename))
            )
