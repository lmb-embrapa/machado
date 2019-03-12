# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Tests command load publication."""

import os
from django.test import TestCase
from django.core.exceptions import ObjectDoesNotExist
from django.core.management import call_command
from django.core.management.base import CommandError
from machado.models import Pub


class CommandTest(TestCase):
    """Tests Commands - load publication."""

    def test_load_publication(self):
        """Tests - load publication."""
        # test load publication
        directory = os.path.dirname(os.path.abspath(__file__))
        file = os.path.join(directory, 'data', 'reference.bib')
        call_command("load_publication",
                     "--file={}".format(file),
                     "--verbosity=0")
        self.assertTrue(Pub.objects.get(
            volume='113'))

        # test ImportingError
        with self.assertRaises(CommandError):
            call_command("load_publication",
                         "--file=does_not_exist",
                         "--verbosity=0")

        # test remove publication
        call_command("remove_publication",
                     "--doi=10.1073/pnas.1604560113",
                     "--verbosity=0")
        with self.assertRaises(ObjectDoesNotExist):
            Pub.objects.get(volume='113')

        # test remove publication does not exist
        with self.assertRaisesMessage(
                    CommandError,
                    'DOI does not exist in database'):
            call_command("remove_publication",
                         "--doi=10.1073/pnas.1604560113",
                         "--verbosity=0")
