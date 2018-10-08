# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Load OrthoMCL groups.txt result."""

from Bio import SeqIO
from machado.loaders.common import FileValidator
from machado.loaders.orthology import OrthologyLoader
from machado.loaders.exceptions import ImportingError
from machado.models import Cv, Db, Cvterm, Dbxref, Dbxrefprop
from machado.models import Feature, FeatureCvterm, FeatureDbxref, Featureloc
from machado.models import Featureprop, FeatureSynonym, FeatureRelationship
from machado.models import Organism, Pub, PubDbxref, FeaturePub, Synonym
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.core.management.base import BaseCommand, CommandError
from tqdm import tqdm
import os, re


class Command(BaseCommand):
    """Load OrthoMCL groups.txt results."""

    help = 'Load "groups.txt" output result file from orthoMCL'

    def add_arguments(self, parser):
        """Define the arguments."""
        parser.add_argument("--filename", help="'groups.txt' File", required=True,
                            type=str)
        parser.add_argument("--cpu", help="Number of threads", default=1,
                            type=int)

    def handle(self,
               filename: str,
               cpu: int=1,
               verbosity: int=1,
               **options):
        """Execute the main function."""
        if verbosity > 0:
            self.stdout.write('Preprocessing')

        try:
            FileValidator().validate(filename)
        except ImportingError as e:
            raise CommandError(e)

        try:
            groups = open(filename, 'r')
            # retrieve only the file name
            groups_txt = os.path.basename(filename)
            groups_file = OrthologyLoader(groups_txt)
        except ImportingError as e:
            raise CommandError(e)

        pool = ThreadPoolExecutor(max_workers=cpu)
        tasks = list()
        for line in groups:
            # array with protein IDs from a given orthologous group
            members = []
            name = ''
            fields = re.split('\s+', line)
            if re.search('^(\w+)\:$', fields[0]):
                group_field = re.match('^(\w+)\:$', fields[0])
                name = group_field.group(1)
                fields.pop(0)
                for field in fields:
                    if re.search('\|', field):
                        member_field = re.split('\|', field)
                        species = member_field[0]
                        ident = member_field[1]
                        members.append(ident)
            # only orthologous groups with 2 or more members allowed
            if len(members)>1:
                tasks.append(pool.submit(
                    groups_file.store_orthologous_group, name, members))
                # tasks.append(pool.submit(print(name, members)))
        if verbosity > 0:
            self.stdout.write('Loading')
        for task in tqdm(as_completed(tasks), total=len(tasks)):
            if task.result():
                raise(task.result())
        print("printing IDs excluded: {}".format(groups_file.excluded))
        self.stdout.write(self.style.SUCCESS('Done'))
