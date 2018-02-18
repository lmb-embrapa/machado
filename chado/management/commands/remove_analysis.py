"""Remove analysis."""

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from chado.models import Analysis, Analysisfeature, Feature, Featureloc


class Command(BaseCommand):
    """Remove analysis."""

    help = 'Remove analysis (CASCADE)'

    def add_arguments(self, parser):
        """Define the arguments."""
        parser.add_argument("--name", help="db.name", required=True, type=str)

    def handle(self, name: str, **options):
        """Execute the main function."""
        try:
            self.stdout.write('Deleting {} and every child record (CASCADE)'
                              .format(name))

            analysis = Analysis.objects.get(sourcename=name)

            feature_ids = Analysisfeature.objects.filter(
                analysis=analysis).values_list('feature_id', flat=True)

            Featureloc.objects.filter(feature_id__in=feature_ids).delete()
            Analysisfeature.objects.filter(analysis=analysis).delete()
            Feature.objects.filter(feature_id__in=feature_ids).delete()
            analysis.delete()

            self.stdout.write(self.style.SUCCESS('Done'))
        except ObjectDoesNotExist:
            raise CommandError(
                    'Cannot remove {} (not registered)'.format(name))
