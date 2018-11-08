# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Load RNA-seq information .csv file."""

from machado.loaders.common import FileValidator, FieldsValidator
from machado.loaders.common import retrieve_organism
from machado.loaders.assay import AssayLoader
from machado.loaders.project import ProjectLoader
from machado.loaders.biomaterial import BiomaterialLoader
from machado.loaders.treatment import TreatmentLoader
from machado.loaders.exceptions import ImportingError
from machado.models import Db, Dbxref, Cv, Cvterm
from machado.models import Biomaterial, Project, Treatment
from machado.models import Assay, Arraydesign, Protocol, Contact
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from tqdm import tqdm
import re


class Command(BaseCommand):
    """Load RNA-seq information file."""

    help = """Load RNA-seq .csv information file. The input file should be
    headless and have the following columns:

    Organism,ProjectAcc,BiomaterialAcc,AssayAcc,Condition,Tissue,Date

    Example of a line sampled from such a file:

    Orysa sativa,GSE85653,GSM2280286,SRR4033018,Heat,leaf,May-30-2018

    The information about the database related to the project, biomaterial
    and assay accessions (e.g: "SRA") need to be provided from command line."""

    def add_arguments(self, parser):
        """Define the arguments."""
        parser.add_argument("--filename",
                            help="'.csv' file with sample and projects info.",
                            required=True,
                            type=str)
        parser.add_argument("--projectdb",
                            help="Project database info (e.g.: 'GEO')",
                            required=True,
                            type=str)
        parser.add_argument("--biomaterialdb",
                            help="Biomaterial database info (e.g.: 'GEO')",
                            required=True,
                            type=str)
        parser.add_argument("--assaydb",
                            help="Assay database info (e.g.: 'SRA')",
                            required=True,
                            type=str)
        parser.add_argument("--cpu",
                            help="Number of threads",
                            default=1,
                            type=int)

    def handle(self,
               filename: str,
               projectdb: str,
               biomaterialdb: str,
               assaydb: str,
               cpu: int=1,
               verbosity: int=0,
               **options):
        """Execute the main function."""
        nfields = 7
        if verbosity > 0:
            self.stdout.write('Preprocessing')
        try:
            FileValidator().validate(filename)
        except ImportingError as e:
            raise CommandError(e)

        try:
            rnaseq_data = open(filename, 'r')
            # retrieve only the file name
        except ImportingError as e:
            raise CommandError(e)

        # instantiate project, biomaterial and assay
        try:
            project = ProjectLoader(db=projectdb)
            biomaterial = BiomaterialLoader(db=biomaterialdb)
            assay = AssayLoader(db=assaydb)
            treatment = TreatmentLoader()
        except ImportingError as e:
            raise CommandError(e)

        # each line is an RNA-seq experiment
        # e.g:
        # Oryza sativa,GSE112368,GSM3068810,SRR6902930,heat,leaf,Jul-20-2018
        for line in rnaseq_data:
            fields = re.split(',', line.strip())
            try:
                FieldsValidator().validate(nfields, fields)
            except ImportingError as e:
                raise CommandError(e)
            # get organism - mandatory
            try:
                organism = retrieve_organism(organism=fields[0])
            except ObjectDoesNotExist as e:
                raise ImportingError(e)
            # store project
            try:
                # e.g: "GSExxx" from GEO
                project.store_project(name=fields[1])
                # project_dbxref is same as project (refers to accession:
                # e.g: "GSExxx" from GEO)
                project.store_project_dbxref(acc=fields[1])
            except ObjectDoesNotExist as e:
                raise ImportingError(e)

            # store biomaterial (sample)
            try:
                # e.g: "GSMxxxx" from GEO
                biomaterial.store_biomaterial(
                    acc=fields[2],
                    organism=organism,
                    name=fields[2],
                    description=fields[5])
            except ImportingError as e:
                raise CommandError(e)
            # store treatment
            try:
                # e.g. "Heat"
                treatment.store_treatment(
                        name=fields[4],
                        biomaterial=biomaterial.biomaterial)
                biomaterial.store_biomaterial_treatment(
                        treatment=treatment.treatment)
            except ImportingError as e:
                raise CommandError(e)

            # store assay (experiment)
            try:
                # e.g. "SRRxxxx" from GEO
                assay.store_assay(
                    acc=fields[3],
                    assaydate=fields[6],
                    name=fields[3],
                    description=fields[3])
                assay.store_assay_project(
                    project=project.project)
                assay.store_assay_biomaterial(
                    biomaterial=biomaterial.biomaterial)
            except ImportingError as e:
                raise CommandError(e)
        self.stdout.write(self.style.SUCCESS('Done'))
