"""Remove analysis."""

from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from chado.models import Analysis, Analysisfeature, Featureloc


class Command(BaseCommand):
    """Remove analysis."""

    help = 'Remove analysis (CASCADE)'

    def add_arguments(self, parser):
        """Define the arguments."""
        parser.add_argument("--name", help="db.name", required=True, type=str)

    def handle(self, *args, **options):
        """Execute the main function."""
        try:
            self.stdout.write('Deleting %s and every child record (CASCADE)'
                              % (options['name']))

            analysis = Analysis.objects.get(sourcename=options['name'])
            Analysisfeature.objects.filter(analysis=analysis).delete()
            Featureloc.objects.filter(locgroup=analysis.analysis_id).delete()
            analysis.delete()

            self.stdout.write(self.style.SUCCESS('Done'))
        except ObjectDoesNotExist:
            self.stdout.write(self.style.ERROR(
                'Cannot remove %s (not registered)' % (options['name'])))
