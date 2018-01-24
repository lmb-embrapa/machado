"""Tests Libraries."""

from chado.models import Db
from chado.lib.db import get_set_db
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
