"""Tests Libraries."""

from chado.models import Db, Dbxref
from chado.lib.db import get_set_db, set_db_file
from chado.lib.dbxref import get_set_dbxref, get_dbxref
from django.test import TestCase


class DbLibTest(TestCase):
    """Tests Libraries - DB."""

    def test_get_set_db_new(self):
        """Tests - get_set_db - new."""
        test_db = get_set_db(db_name='test_name',
                             description='test_description',
                             urlprefix='test_urlprefix',
                             url='test_url')
        self.assertEqual('test_name', test_db.name)
        self.assertEqual('test_description', test_db.description)
        self.assertEqual('test_urlprefix', test_db.urlprefix)
        self.assertEqual('test_url', test_db.url)

    def test_get_set_db_existing(self):
        """Tests - get_set_db - existing."""
        Db.objects.create(name='test_name',
                          description='test_description',
                          urlprefix='test_urlprefix',
                          url='test_url')

        test_db = get_set_db(db_name='test_name',
                             description='test_description',
                             urlprefix='test_urlprefix',
                             url='test_url')
        self.assertEqual('test_name', test_db.name)
        self.assertEqual('test_description', test_db.description)
        self.assertEqual('test_urlprefix', test_db.urlprefix)
        self.assertEqual('test_url', test_db.url)

    def test_set_db_file(self):
        """Tests - set_db_file."""
        test_db = set_db_file(file='/tmp/test_name.file')
        self.assertEqual('test_name.file', test_db.name)


class DbxrefLibTest(TestCase):
    """Tests Libraries - DBxref."""

    def test_get_set_dbxref_new(self):
        """Tests - get_set_dbxref - new."""
        test_dbxref = get_set_dbxref(db_name='test_db_name',
                                     accession='test_accession',
                                     description='test_description',
                                     version='test_version')
        self.assertEqual('test_accession', test_dbxref.accession)
        self.assertEqual('test_description', test_dbxref.description)
        self.assertEqual('test_version', test_dbxref.version)

    def test_get_set_dbxref_existing(self):
        """Tests - get_set_dbxref - existing."""
        db = Db.objects.create(name='test_db_name',
                               description='test_description',
                               urlprefix='test_urlprefix',
                               url='test_url')
        Dbxref.objects.create(db=db,
                              accession='test_accession',
                              description='test_description',
                              version='test_version')

        test_dbxref = get_set_dbxref(db_name='test_db',
                                     accession='test_accession',
                                     description='test_description',
                                     version='test_version')
        self.assertEqual('test_accession', test_dbxref.accession)
        self.assertEqual('test_description', test_dbxref.description)
        self.assertEqual('test_version', test_dbxref.version)

    def test_get_dbxref(self):
        """Tests - get_dbxref."""
        db = Db.objects.create(name='test_db_name',
                               description='test_description',
                               urlprefix='test_urlprefix',
                               url='test_url')
        Dbxref.objects.create(db=db,
                              accession='test_accession',
                              description='test_description',
                              version='test_version')

        test_dbxref = get_dbxref(db_name='test_db_name',
                                 accession='test_accession')
        self.assertEqual('test_accession', test_dbxref.accession)
        self.assertEqual('test_description', test_dbxref.description)
        self.assertEqual('test_version', test_dbxref.version)
