from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from chado.models import Db


class Command(BaseCommand):
    help = 'Remove Db (CASCADE)'

    def add_arguments(self, parser):
        parser.add_argument("--name", help="db.name", required=True, type=str)

    def handle(self, *args, **options):

        try:
            db = Db.objects.get(name=options['name'])

            self.stdout.write('Deleting %s and every child record (CASCADE)'
                              % (options['name']))

            db.delete()

            self.stdout.write(self.style.SUCCESS('Done'))
        except ObjectDoesNotExist:
            self.stdout.write(self.style.ERROR(
                'Cannot remove %s (not registered)' % (options['name'])))
