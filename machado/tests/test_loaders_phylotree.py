# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Tests phylotree loader."""

from django.core.management import call_command
from django.test import TestCase

from machado.loaders.organism import OrganismLoader
from machado.loaders.phylotree import PhylotreeLoader
from machado.models import Organism, Phylonode, Phylotree


class PhylotreeTest(TestCase):
    """Tests phylotree loader."""

    def test_store_type_def(self):
        """Tests - store type_def."""
        organism_db = OrganismLoader("testOrganism")

        organism_db.store_organism_record(
            taxid=1, scname="root", synonyms=[], common_names=[]
        )
        organism_db.store_organism_record(
            taxid=2, scname="Ilex", synonyms=[], common_names=[]
        )
        organism_db.store_organism_record(
            taxid=3, scname="Ilex paraguariensis", synonyms=[], common_names=[]
        )
        organism_db.store_organism_record(
            taxid=4, scname="Ilex montana", synonyms=[], common_names=[]
        )

        tree = {
            1: {
                "parent_id": None,
                "level": "no rank",
                "children": [1, 2],
                "left_idx": 1,
                "right_idx": 8,
            },
            2: {
                "parent_id": 1,
                "level": "genus",
                "children": [3, 4],
                "left_idx": 2,
                "right_idx": 7,
            },
            3: {
                "parent_id": 2,
                "level": "species",
                "children": [],
                "left_idx": 3,
                "right_idx": 6,
            },
            4: {
                "parent_id": 2,
                "level": "species",
                "children": [],
                "left_idx": 4,
                "right_idx": 5,
            },
        }

        phylotree = PhylotreeLoader(
            phylotree_name="testTaxonomy", organism_db="testOrganism"
        )

        for key, data in tree.items():
            tax_id, phylonode = phylotree.store_phylonode_record(
                tax_id=key,
                parent_id=None,
                level=data["level"],
                left_idx=data["left_idx"],
                right_idx=data["right_idx"],
            )
            tree[tax_id]["phylonode_id"] = phylonode.phylonode_id

        for key, data in tree.items():
            if data.get("parent_id") is None:
                continue
            phylotree.update_parent_phylonode_id(
                data["phylonode_id"], data["parent_id"]
            )

        test_organism1 = Organism.objects.get(genus="Ilex", species=".spp")
        test_phylonode1 = Phylonode.objects.get(
            PhylonodeOrganism_phylonode_Phylonode__organism=test_organism1
        )

        test_organism2 = Organism.objects.get(genus="Ilex", species="paraguariensis")
        test_phylonode2 = Phylonode.objects.get(
            PhylonodeOrganism_phylonode_Phylonode__organism=test_organism2
        )

        self.assertEqual(3, test_phylonode2.left_idx)
        self.assertEqual(6, test_phylonode2.right_idx)
        self.assertEqual(
            test_phylonode1.phylonode_id, test_phylonode2.parent_phylonode_id
        )
        # test remove_phylotree
        self.assertTrue(Phylotree.objects.filter(name="testTaxonomy").exists())
        call_command("remove_phylotree", "--name=testTaxonomy", "--verbosity=0")
        self.assertFalse(Phylotree.objects.filter(name="testTaxonomy").exists())
