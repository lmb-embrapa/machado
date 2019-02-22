# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Remove relationship."""

from machado.models import Cvterm, FeatureRelationship, FeatureRelationshipprop
from machado.loaders.exceptions import ImportingError
from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
from tqdm import tqdm


class Command(BaseCommand):
    """Remove relationship."""

    help = 'Remove relationship'

    def add_arguments(self, parser):
        """Define the arguments."""
        parser.add_argument("--filename",
                            help="name of the file (e.g.: groups.txt",
                            required=True,
                            type=str)

    def handle(self,
               filename: str,
               verbosity: int = 1,
               **options):
        """Execute the main function."""
        # get cvterm for contained in
        try:
            cvterm_contained_in = Cvterm.objects.get(
                name='contained in', cv__name='relationship')
        except IntegrityError as e:
            raise ImportingError(e)
        try:
            frps = FeatureRelationshipprop.objects.filter(
                    value=filename,
                    type_id=cvterm_contained_in.cvterm_id)
            if verbosity > 0:
                self.stdout.write(
                        'Deleting every relationship relations from {}'
                        .format(filename))
            # get all feature_relationship_id and
            # remove all feature_relationshipprop
            for frp in tqdm(frps, total=len(frps)):
                fr = FeatureRelationship.objects.get(
                        feature_relationship_id=frp.feature_relationship_id)
                frp.delete()
                fr.delete()
            # remove all feature_relationships
            if verbosity > 0:
                self.stdout.write(self.style.SUCCESS('Done'))
        except IntegrityError as e:
            raise CommandError(
                    'It\'s not possible to delete every record. You must '
                    'delete relationships loaded after \'{}\' that might '
                    'depend on it. {}'.format(filename, e))
        except ObjectDoesNotExist:
            raise CommandError(
                    'Cannot remove \'{}\' (not registered)'.format(filename))
