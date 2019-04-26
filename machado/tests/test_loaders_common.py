# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Tests Loaders - Common."""

import os

from django.test import TestCase

from machado.loaders.common import FileValidator
from machado.loaders.common import insert_organism, retrieve_organism
from machado.loaders.exceptions import ImportingError
from machado.models import Cv, Cvterm, Db, Dbxref, Organism


class CommonTest(TestCase):
    """Tests Loaders - Common."""

    def test_insert_organism_1(self):
        """Tests - insert_organism."""
        # test insert organism simple
        insert_organism(genus="Mus", species="musculus")
        test_organism_1 = Organism.objects.get(genus="Mus", species="musculus")
        self.assertEqual("Mus", test_organism_1.genus)
        self.assertEqual("musculus", test_organism_1.species)

        # test organism already registered
        with self.assertRaisesMessage(
            ImportingError, "Organism already registered (Mus musculus)!"
        ):
            insert_organism(genus="Mus", species="musculus")

        # test insert organism complete
        test_db = Db.objects.create(name="test_db")
        test_dbxref = Dbxref.objects.create(accession="test_dbxref", db=test_db)

        test_cv = Cv.objects.create(name="test_cv")
        Cvterm.objects.create(
            name="test_cvterm",
            cv=test_cv,
            dbxref=test_dbxref,
            is_obsolete=0,
            is_relationshiptype=0,
        )
        insert_organism(
            genus="Homo",
            species="sapiens",
            abbreviation="hs",
            common_name="human",
            comment="no comments",
        )
        test_organism_2 = Organism.objects.get(genus="Homo", species="sapiens")
        self.assertEqual("Homo", test_organism_2.genus)
        self.assertEqual("sapiens", test_organism_2.species)
        self.assertEqual("hs", test_organism_2.abbreviation)
        self.assertEqual("human", test_organism_2.common_name)
        self.assertEqual("no comments", test_organism_2.comment)

    def test_retrieve_organism(self):
        """Tests - retrieve organism."""
        insert_organism(genus="Bos")
        insert_organism(genus="Bos", species="taurus")
        insert_organism(genus="Bos", species="taurus", infraspecific_name="indicus")
        test_organism = retrieve_organism("Bos")
        self.assertEqual("Bos", test_organism.genus)
        test_organism = retrieve_organism("Bos taurus")
        self.assertEqual("taurus", test_organism.species)
        test_organism = retrieve_organism("Bos taurus indicus")
        self.assertEqual("indicus", test_organism.infraspecific_name)

    def test_validate_file(self):
        """Tests - validate file."""
        # test file not exists
        file_path = "/tmp/machado.test.file"
        v = FileValidator()
        with self.assertRaisesMessage(
            ImportingError, "{} does not exist".format(file_path)
        ):
            v.validate(file_path=file_path)

        # test wrong file type
        file_path = "/tmp/machado.test.dir"
        os.mkdir(file_path)
        v = FileValidator()
        with self.assertRaisesMessage(
            ImportingError, "{} is not a file".format(file_path)
        ):
            v.validate(file_path=file_path)
        os.rmdir(file_path)

        # test file not readable
        file_path = "/tmp/machado.test.file"
        os.mknod(file_path, mode=0o200)
        v = FileValidator()
        with self.assertRaisesMessage(
            ImportingError, "{} is not readable".format(file_path)
        ):
            v.validate(file_path=file_path)
        os.remove(file_path)
