# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Load OrthoMCL groups.txt result."""

from machado.loaders.common import FileValidator
from machado.loaders.common import get_num_lines
from machado.loaders.exceptions import ImportingError
from machado.loaders.feature import FeatureLoader
from machado.models import Cvterm, Organism
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.core.management.base import BaseCommand, CommandError
from tqdm import tqdm
import re
import os


class Command(BaseCommand):
    """Load OrthoMCL groups.txt results."""

    help = """Load 'groups.txt' output result file from orthoMCL.
The 'groups.txt' file is headless and have the format as follows:
nameofthegroup1: featuremember1 featuremember2 featuremember3
nameofthegroup2: featuremember4 featuremember5 ...
and so on.
The feature members need to be loaded previously."""

    def add_arguments(self, parser):
        """Define the arguments."""
        parser.add_argument("--file",
                            help="'groups.txt' File",
                            required=True,
                            type=str)
        parser.add_argument("--cpu",
                            help="Number of threads",
                            default=1,
                            type=int)

    def handle(self,
               file: str,
               cpu: int = 1,
               verbosity: int = 0,
               **options):
        """Execute the main function."""
        try:
            FileValidator().validate(file)
        except ImportingError as e:
            raise CommandError(e)
        filename = os.path.basename(file)
        if verbosity > 0:
            self.stdout.write('Processing file: {}'.format(filename))
        try:
            groups = open(file, 'r')
            # retrieve only the file name
        except ImportingError as e:
            raise CommandError(e)
        pool = ThreadPoolExecutor(max_workers=cpu)
        tasks = list()
        cvterm_cluster = Cvterm.objects.get(
            name='in orthology relationship with', cv__name='relationship')
        organism, created = Organism.objects.get_or_create(
                    abbreviation='multispecies',
                    genus='multispecies',
                    species='multispecies',
                    common_name='multispecies')
        source = "null"
        featureloader = FeatureLoader(
                source=source,
                filename=filename,
                organism=organism)
        # each line is an orthologous group
        for line in tqdm(groups, total=get_num_lines(file)):
            members = []
            name = ''
            fields = re.split(r'\s+', line.strip())
            if re.search(r'^(\w+)\:', fields[0]):
                group_field = re.match(r'^(\w+)\:', fields[0])
                name = group_field.group(1)
                fields.pop(0)
                for field in fields:
                    if re.search(r'^(\w+)\|(\S+)', field):
                        member_field = re.match(r'^(\w+)\|(\S+)', field)
                        # species = member_field.group(1)
                        ident = member_field.group(2)
                        members.append(ident)
            else:
                raise CommandError("Cluster has no identification, check.")
            # only orthologous groups with 2 or more members allowed
            if len(members) > 1:
                tasks.append(
                    pool.submit(
                            featureloader.store_feature_relationships_group,
                            members,
                            cvterm_cluster,
                            name))
        if verbosity > 0:
            self.stdout.write('Loading')
        for task in tqdm(as_completed(tasks), total=len(tasks)):
            if task.result():
                raise(task.result())
        pool.shutdown()
        if verbosity > 0:
            self.stdout.write(self.style.SUCCESS(
                'Done with {}'.format(filename)))
