"""Load phylonodes file."""

from chado.loaders.common import FileValidator
from chado.loaders.exceptions import ImportingError
from chado.loaders.phylotree import PhylotreeLoader
from django.core.management.base import BaseCommand, CommandError
import re


class Command(BaseCommand):
    """Load organism file."""

    help = 'Load phylonodes file'

    def add_arguments(self, parser):
        """Define the arguments."""
        parser.add_argument("--nodes", help="names file <e.g.: nodes.dmp>",
                            required=True, type=str)

    def walktree(self, node_id: int):
        """Walk the tree setting left_idx and right_idx."""
        self.ctr += 1
        self.nodes[node_id]['left_idx'] = self.ctr
        for child_id in self.nodes[node_id]['children']:
            if node_id == child_id:
                self.nodes[node_id]['parent_id'] = None
                continue
            self.walktree(child_id)
        self.ctr += 1
        self.nodes[node_id]['right_idx'] = self.ctr

    def walktree_store(self, phylotree: PhylotreeLoader, node_id: int):
        """Walk the tree to store data in valid order."""
        self.ctr += 1
        if self.ctr % 10000 == 0:
            self.stdout.write(' {} nodes loaded'.format(self.ctr))
        data = self.nodes[node_id]
        phylotree.store_phylonode_record(
            tax_id=node_id,
            parent_id=data['parent_id'],
            level=data['level'],
            left_idx=data['left_idx'],
            right_idx=data['right_idx'])

        for child_id in self.nodes[node_id]['children']:
            if node_id == child_id:
                continue
            self.walktree_store(phylotree, child_id)

    def handle(self,
               nodes: str,
               verbosity: int=1,
               cpu: int=1,
               **options):
        """Execute the main function."""
        if verbosity > 0:
            self.stdout.write('Preprocessing')

        try:
            FileValidator().validate(nodes)
        except ImportingError as e:
            raise CommandError(e)

        try:
            phylotree = PhylotreeLoader(
                phylotree_name='NCBI taxonomy tree')
        except ImportingError as e:
            raise CommandError(e)

        file_nodes = open(nodes)

        self.nodes = dict()
        self.ctr = 0
        for line in file_nodes:
            columns = re.split('\s\|\s', line)
            tax_id = int(columns[0])
            parent_id = int(columns[1])
            level = columns[2]

            if self.nodes.get(tax_id) is None:
                self.nodes[tax_id] = {'parent_id': parent_id,
                                      'level': level,
                                      'children': []}
            else:
                self.nodes[tax_id]['parent_id'] = parent_id
                self.nodes[tax_id]['level'] = level
            if self.nodes.get(parent_id) is None:
                self.nodes[parent_id] = {'parent_id': None,
                                         'level': None,
                                         'children': [tax_id]}
            else:
                self.nodes[parent_id]['children'].append(tax_id)

        self.walktree(1)

        if verbosity > 0:
            self.stdout.write('Loading')
        self.ctr = 0
        self.walktree_store(phylotree, 1)

        self.stdout.write(self.style.SUCCESS('Done'))
