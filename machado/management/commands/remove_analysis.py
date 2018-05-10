# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Remove analysis."""

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from machado.models import Analysis, Analysisfeature, Feature, Featureloc


class Command(BaseCommand):
    """Remove analysis."""

    help = 'Remove analysis (CASCADE)'

    def add_arguments(self, parser):
        """Define the arguments."""
        parser.add_argument("--name", help="analysis.sourcename",
                            required=True, type=str)

    def handle(self,
               name: str,
               verbosity: int=1,
               **options):
        """Execute the main function."""
        try:
            if verbosity > 0:
                self.stdout.write('Deleting {} and every child'
                                  'record (CASCADE)'.format(name))

            analysis = Analysis.objects.get(sourcename=name)

            feature_ids = list(Analysisfeature.objects.filter(
                analysis=analysis).values_list('feature_id', flat=True))

            Featureloc.objects.filter(feature_id__in=feature_ids).delete()
            Analysisfeature.objects.filter(analysis=analysis).delete()
            Feature.objects.filter(feature_id__in=feature_ids).delete()
            analysis.delete()
            if verbosity > 0:
                self.stdout.write(self.style.SUCCESS('Done'))
        except ObjectDoesNotExist:
            raise CommandError(
                    'Cannot remove {} (not registered)'.format(name))
