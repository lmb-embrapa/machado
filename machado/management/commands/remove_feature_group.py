# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Remove relationship."""

from machado.models import Cvterm, Featureprop
from machado.loaders.exceptions import ImportingError
from machado.loaders.common import retrieve_organism
from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError


class Command(BaseCommand):
    """Remove feature group."""

    help = 'Remove feature group'

    def add_arguments(self, parser):
        """Define the arguments."""
        parser.add_argument("--term",
                            help="cvterm (e.g.: 'coexpression group')",
                            required=True,
                            type=str)
        parser.add_argument("--organism",
                            help="Scientific name (e.g.: 'Oryza sativa')",
                            required=True,
                            type=str)

    def handle(self,
               term: str,
               organism: str,
               verbosity: int = 0,
               **options):
        """Execute the main function."""
        # retrieve organism
        try:
            organism = retrieve_organism(organism)
        except IntegrityError as e:
            raise ImportingError(e)
        # get cvterm for contained in
        try:
            cvterm_id = Cvterm.objects.get(
                name=term, cv__name='feature_property').cvterm_id
        except IntegrityError as e:
            raise ImportingError(e)
        if verbosity > 0:
            self.stdout.write('Removing ...')
        try:
            Featureprop.objects.filter(
                type_id=cvterm_id,
                feature__organism_id=organism.organism_id).delete()
            if verbosity > 0:
                self.stdout.write('Done.')
        except IntegrityError:
            raise CommandError(
                'Could not delete every record related to: {}'.format(term))
        except ObjectDoesNotExist:
            raise CommandError(
                'No feature related to cvterm {} was found.'.format(term))
