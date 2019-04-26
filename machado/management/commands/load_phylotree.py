# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Load phylonodes file."""

import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict

from django.core.management.base import BaseCommand, CommandError
from tqdm import tqdm

from machado.loaders.common import FileValidator
from machado.loaders.exceptions import ImportingError
from machado.loaders.phylotree import PhylotreeLoader


class Command(BaseCommand):
    """Load phylonodes file."""

    help = """Load phylonodes file. Each phylonode will get a left and right
              indexes, which are calculated by walking down the entire tree
              structure (reference: Chado load_ncbi_taxonomy.pl)"""

    def add_arguments(self, parser):
        """Define the arguments."""
        parser.add_argument(
            "--file", help="names file <e.g.: nodes.dmp>", required=True, type=str
        )
        parser.add_argument(
            "--name",
            help="Set a phylotree name " "<e.g.: NCBI taxonomy tree>",
            required=True,
            type=str,
        )
        parser.add_argument(
            "--organismdb",
            help="inform the Organism DB name " "<e.g.: DB:NCBI_taxonomy>",
            required=True,
            type=str,
        )
        parser.add_argument("--cpu", help="Number of threads", default=1, type=int)

    def walktree(self, node_id: int):
        """Walk the tree setting left_idx and right_idx."""
        self.ctr += 1
        self.nodes[node_id]["left_idx"] = self.ctr
        for child_id in self.nodes[node_id]["children"]:
            if node_id == child_id:
                self.nodes[node_id]["parent_id"] = None
                continue
            self.walktree(child_id)
        self.ctr += 1
        self.nodes[node_id]["right_idx"] = self.ctr

    def handle(
        self,
        file: str,
        name: str,
        organismdb: str,
        verbosity: int = 1,
        cpu: int = 1,
        **options
    ):
        """Execute the main function."""
        if verbosity > 0:
            self.stdout.write("Preprocessing")

        try:
            FileValidator().validate(file)
        except ImportingError as e:
            raise CommandError(e)

        try:
            phylotree = PhylotreeLoader(phylotree_name=name, organism_db=organismdb)
        except ImportingError as e:
            raise CommandError(e)

        file_nodes = open(file)

        self.nodes: Dict[int, Dict[str, Any]] = dict()
        self.ctr = 0
        for line in file_nodes:
            columns = re.split("\s\|\s", line)
            tax_id = int(columns[0])
            parent_id = int(columns[1])
            level = columns[2]

            if self.nodes.get(tax_id) is None:
                self.nodes[tax_id] = {
                    "parent_id": parent_id,
                    "level": level,
                    "children": [],
                }
            else:
                self.nodes[tax_id]["parent_id"] = parent_id
                self.nodes[tax_id]["level"] = level
            if self.nodes.get(parent_id) is None:
                self.nodes[parent_id] = {
                    "parent_id": None,
                    "level": None,
                    "children": [tax_id],
                }
            else:
                self.nodes[parent_id]["children"].append(tax_id)

        self.walktree(node_id=1)

        if verbosity > 0:
            self.stdout.write("Loading")

        pool = ThreadPoolExecutor(max_workers=cpu)
        tasks = list()
        # By setting the parent_id to None it's possible to load the
        # nodes randomly and using threads.
        try:
            for key, data in self.nodes.items():
                tasks.append(
                    pool.submit(
                        phylotree.store_phylonode_record,
                        tax_id=key,
                        parent_id=None,
                        level=data["level"],
                        left_idx=data["left_idx"],
                        right_idx=data["right_idx"],
                    )
                )
            for task in tqdm(as_completed(tasks), total=len(tasks)):
                if task.result():
                    tax_id, phylonode = task.result()
                    self.nodes[tax_id]["phylonode_id"] = phylonode.phylonode_id
        except KeyError as e:
            raise CommandError(
                "Could not calculate {}. Make it sure it is "
                "possible to walk the entire tree "
                "structure.".format(e)
            )

        if verbosity > 0:
            self.stdout.write("Loading nodes relationships")
        tasks = list()
        # Load the nodes relationship info
        for key, data in self.nodes.items():
            if data.get("parent_id") is None:
                continue
            tasks.append(
                pool.submit(
                    phylotree.update_parent_phylonode_id,
                    data["phylonode_id"],
                    data["parent_id"],
                )
            )
        for task in tqdm(as_completed(tasks), total=len(tasks)):
            if task.result():
                raise (task.result())
        pool.shutdown()

        if verbosity > 0:
            self.stdout.write(self.style.SUCCESS("Done"))
