"""Tests Models."""

from django.test import TestCase
from chado.models import Db


class DbModelTest(TestCase):
    """Tests Models - DB."""

    def test_DB(self):
        """Tests - DB."""
        test_db = Db.objects.create(
            name='test_name',
            description='test_description',
            urlprefix='test_urlprefix',
            url='test_url'
        )
        self.assertEqual('test_name', test_db.name)
