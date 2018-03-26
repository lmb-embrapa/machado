"""Remove file."""

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from machado.models import Dbxref, Dbxrefprop
from machado.models import Feature, Featureloc, FeatureDbxref
from machado.models import Featureprop, FeatureRelationship, FeatureSynonym
from machado.models import FeatureCvterm


class Command(BaseCommand):
    """Remove file."""

    help = 'Remove file (CASCADE)'

    def add_arguments(self, parser):
        """Define the arguments."""
        parser.add_argument(
            "--name", help="File name", required=True, type=str)

    def handle(self, name: str, **options):
        """Execute the main function."""
        try:
            self.stdout.write('Deleting {} and every child record (CASCADE)'
                              .format(name))

            dbxref_ids = list(Dbxrefprop.objects.filter(
                value=name).values_list('dbxref_id', flat=True))
            feature_ids = list(Feature.objects.filter(
                dbxref_id__in=dbxref_ids).values_list('feature_id', flat=True))
            Featureloc.objects.filter(feature_id__in=feature_ids).delete()
            Featureprop.objects.filter(feature_id__in=feature_ids).delete()
            FeatureSynonym.objects.filter(feature_id__in=feature_ids).delete()
            FeatureCvterm.objects.filter(feature_id__in=feature_ids).delete()
            FeatureDbxref.objects.filter(feature_id__in=feature_ids).delete()
            FeatureRelationship.objects.filter(
                object_id__in=feature_ids).delete()
            FeatureRelationship.objects.filter(
                subject_id__in=feature_ids).delete()
            Feature.objects.filter(dbxref_id__in=dbxref_ids).delete()
            Dbxrefprop.objects.filter(value=name).delete()
            Dbxref.objects.filter(dbxref_id__in=dbxref_ids).delete()

            self.stdout.write(self.style.SUCCESS('Done'))
        except ObjectDoesNotExist:
            raise CommandError(
                'Cannot remove {} (not registered)'.format(name))
