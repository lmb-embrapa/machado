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
from machado.loaders.exceptions import ImportingError
from machado.models import Db, Dbxref, Cv, Cvterm
from machado.models import Biomaterial, Project
from machado.models import Assay, Arraydesign, Protocol, Contact
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.core.management.base import BaseCommand, CommandError
from tqdm import tqdm
import re


class Command(BaseCommand):
    """Load RNA-seq information file."""

    help = 'Load RNA-seq .csv information file.'
    'The file is headless and should have the following columns:'
    'Organism,ProjectAcc,BiomaterialAcc,AssayAcc,Condition,Tissue,Date'
    'Example of a line sampled from such a file:'
    'Orysa sativa,GSE85653,GSM2280286,SRR4033018,Heat,leaf,May-30-2018'
    'The information about the database related to the project, biomaterial'
    ' and assay accessions (e.g: "SRA") need to be provided from command line.'

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
            self.stdout.write('Number of fields in file should be {}'
                    .format(nfields))
        try:
            FileValidator().validate(filename)
        except ImportingError as e:
            raise CommandError(e)

        try:
            rnaseq_data = open(filename, 'r')
            # retrieve only the file name
        except ImportingError as e:
            raise CommandError(e)

        # each line is an orthologous group
        for line in rnaseq_data:
            fields = re.split(',', line.strip())
            try:
                FieldsValidator().validate(nfields, fields)
            except ImportingError as e:
                raise CommandError(e)
            # get organism
            try:
                organism = retrieve_organism(fields[0])
            except ObjectDoesNotExist as e:
                raise ImportingError(e)

            # get project
            project = Union[fields[1], Project]
            if not isinstance(project, Project):
                try:
                    project = ProjectLoader().store_project(fields[1])
                    project_dbxref = project.store_project_dbxref(
                            db=projectdb,
                            acc=fields[1])
                except ImportingError as e:
                    raise CommandError(e)

            # get biomaterial (sample)
            biomaterial = Union[fields[2], Biomaterial]
            if not isinstance(biomaterial, Biomaterial):
                try:
                    biomaterial = BiomaterialLoader(biomaterialdb)
                    biomaterial.store_biomaterial(
                        acc=fields[2],
                        organism=organism,
                        tissue=fields[5],
                        condition=fields[4])
                except ImportingError as e:
                    raise CommandError(e)

            # get assay (experiment)
            assay = Union[fields[3], Assay]
            if not isinstance(assay, Assay):
                assay = AssayLoader(assaydb)
                # will use acc information for other fields as well
                try:
                    assay.store_assay(
                        acc=fields[3],
                        date=fields[6],
                        name=fields[3],
                        description=fields[3])
                    assay.store_assay_project(project)
                    assay.store_assay_biomaterial(biomaterial)
                except ImportingError as e:
                    raise CommandError(e)
        self.stdout.write(self.style.SUCCESS('Done'))
