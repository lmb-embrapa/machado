# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Load OrthoMCL groups.txt result."""

from machado.loaders.common import FileValidator
from machado.loaders.orthology import OrthologyLoader
from machado.loaders.exceptions import ImportingError
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.core.management.base import BaseCommand, CommandError
from tqdm import tqdm
import re


class Command(BaseCommand):
    """Load OrthoMCL groups.txt results."""

    help = 'Load "groups.txt" output result file from orthoMCL'

    def add_arguments(self, parser):
        """Define the arguments."""
        parser.add_argument("--filename",
                            help="'groups.txt' File",
                            required=True,
                            type=str)
        parser.add_argument("--cpu",
                            help="Number of threads",
                            default=1,
                            type=int)

    def handle(self,
               filename: str,
               cpu: int=1,
               verbosity: int=0,
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
        except ImportingError as e:
            raise CommandError(e)

        pool = ThreadPoolExecutor(max_workers=cpu)
        tasks = list()
        # each line is an orthologous group
        for line in groups:
            members = []
            name = ''
            fields = re.split('\s+', line.strip())
            if re.search('^(\w+)\:', fields[0]):
                group_field = re.match('^(\w+)\:', fields[0])
                name = group_field.group(1)
                group = OrthologyLoader(name, filename)
                fields.pop(0)
                for field in fields:
                    if re.search('^(\w+)\|(\S+)', field):
                        member_field = re.match('^(\w+)\|(\S+)', field)
                        species = member_field.group(1)
                        ident = member_field.group(2)
                        members.append(ident)
            # only orthologous groups with 2 or more members allowed
            if len(members)>1:
                tasks.append(pool.submit(
                           group.store_orthologous_group, members))
        if verbosity > 0:
            self.stdout.write('Loading')
        for task in tqdm(as_completed(tasks), total=len(tasks)):
            if task.result():
                raise(task.result())
        self.stdout.write(self.style.SUCCESS('Done'))
