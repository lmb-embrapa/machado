"""Remove db."""

from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from chado.models import Db, Dbxref, Feature


class Command(BaseCommand):
    """Remove db."""

    help = 'Remove Db (CASCADE)'

    def add_arguments(self, parser):
        """Define the arguments."""
        parser.add_argument("--name", help="db.name", required=True, type=str)

    def handle(self, *args, **options):
        """Execute the main function."""
        try:
            self.stdout.write('Deleting %s and every child record (CASCADE)'
                              % (options['name']))

            db = Db.objects.get(name=options['name'])
            dbxref_ids = Dbxref.objects.filter(
                db=db).values_list('dbxref_id', flat=True)
            Feature.objects.filter(dbxref_id__in=dbxref_ids).delete()
            Dbxref.objects.filter(db=db).delete()
            db.delete()

            self.stdout.write(self.style.SUCCESS('Done'))
        except ObjectDoesNotExist:
            self.stdout.write(self.style.ERROR(
                'Cannot remove %s (not registered)' % (options['name'])))
