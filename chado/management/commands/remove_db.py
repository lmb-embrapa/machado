"""Remove db."""

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from chado.models import Db, Dbxref, Dbxrefprop, Feature, Featureloc
from chado.models import Featureprop, FeatureRelationship, FeatureSynonym
from chado.models import FeatureCvterm, FeatureDbxref


class Command(BaseCommand):
    """Remove db."""

    help = 'Remove Db (CASCADE)'

    def add_arguments(self, parser):
        """Define the arguments."""
        parser.add_argument("--name", help="db.name", required=True, type=str)

    def handle(self, name: str, **options):
        """Execute the main function."""
        try:
            self.stdout.write('Deleting {} and every child record (CASCADE)'
                              .format(name))

            db = Db.objects.get(name=name)
            dbxref_ids = Dbxref.objects.filter(
                db=db).values_list('dbxref_id', flat=True)
            Dbxrefprop.objects.filter(dbxref_id__in=dbxref_ids).delete()
            feature_ids = Feature.objects.filter(
                dbxref_id__in=dbxref_ids).values_list('feature_id', flat=True)
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
            Dbxref.objects.filter(db=db).delete()
            db.delete()

            self.stdout.write(self.style.SUCCESS('Done'))
        except ObjectDoesNotExist:
            raise CommandError(
                'Cannot remove {} (not registered)'.format(name))
