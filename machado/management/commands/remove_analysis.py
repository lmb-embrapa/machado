# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Remove analysis."""

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from machado.models import Analysisprop, Analysis, Analysisfeature
from machado.models import Feature, Featureloc, Organism
from machado.models import Quantification, Acquisition


class Command(BaseCommand):
    """Remove analysis."""

    help = 'Remove analysis (CASCADE). Also remove related features that are'
    'multispecies (features that were loaded from the analysis file only).'

    def add_arguments(self, parser):
        """Define the arguments."""
        parser.add_argument("--name",
                            help="source filename (analysisprop.value)",
                            required=True,
                            type=str)

    def handle(self,
               name: str,
               verbosity: int = 1,
               **options):
        """Execute the main function."""
        if verbosity > 0:
            self.stdout.write('Deleting {} and every child'
                              'record (CASCADE)'.format(name))
        # get multispecies organism
        multiorganism, created = Organism.objects.get_or_create(
                abbreviation='multispecies',
                genus='multispecies',
                species='multispecies',
                common_name='multispecies')
        try:
            analysisprop_list = Analysisprop.objects.filter(value=name)
            for analysisprop in analysisprop_list:
                analysis = Analysis.objects.get(
                        analysis_id=analysisprop.analysis_id)
                # remove quantification and aquisition if exists...
                try:
                    quantification = Quantification.objects.get(
                        analysis=analysis)
                    Acquisition.objects.filter(
                        acquisition_id=quantification.acquisition_id).delete()
                    quantification.delete()
                except ObjectDoesNotExist:
                    pass
                # remove analysisfeatures and others if exists...
                try:
                    analysisfeature_list = Analysisfeature.objects.filter(
                            analysis=analysis)
                    for analysisfeature in analysisfeature_list:
                        feature_ids = list(Feature.objects.filter(
                                feature_id=analysisfeature.feature_id,
                                organism=multiorganism).values_list(
                                    'feature_id', flat=True))
                        Featureloc.objects.filter(
                                feature_id__in=feature_ids).delete()
                        Feature.objects.filter(
                                feature_id__in=feature_ids).delete()
                        analysisfeature.delete()
                except ObjectDoesNotExist:
                    pass
                # finally removes analysis...
                analysis.delete()
            if verbosity > 0:
                self.stdout.write(self.style.SUCCESS('Done'))
        except ObjectDoesNotExist:
            raise CommandError(
                    'Cannot remove {} (not registered)'.format(name))
