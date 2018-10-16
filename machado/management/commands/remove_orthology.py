# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Remove orthology."""

from machado.models import Cv, Cvterm
from machado.models import Feature, FeatureRelationship
from machado.models import Dbxref
from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError


class Command(BaseCommand):
    """Remove orthology."""

    help = 'Remove Orthology'

    def add_arguments(self, parser):
        """Define the arguments."""
        parser.add_argument("--name",
                            help="groups.txt",
                            required=True,
                            type=str)

    def handle(self,
               name: str,
               verbosity: int=1,
               **options):
        """Execute the main function."""
        try:
            frs = FeatureRelationship.objects.filter(value=name)
            if verbosity > 0:
                self.stdout.write(
                        'Deleting every orthology relations from {}'
                        .format(name))
            for fr in frs:
                fr.delete()
            if verbosity > 0:
                self.stdout.write(self.style.SUCCESS('Done'))
        except IntegrityError as e:
            raise CommandError(
                    'It\'s not possible to delete every record. You must '
                    'delete orthologies loaded after \'{}\' that might depend '
                    'on it. {}'.format(name, e))
        except ObjectDoesNotExist:
            raise CommandError(
                    'Cannot remove \'{}\' (not registered)'.format(name))
