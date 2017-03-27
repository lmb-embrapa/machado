from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from chado.models import Cv,Cvterm,CvtermDbxref,Dbxref

class Command(BaseCommand):
    help = 'Remove Ontology (CASCADE)'

    def add_arguments(self, parser):
        parser.add_argument("--name", help="cv.name", required = True, type=str)
        parser.add_argument("--definition", help="cv.definition", required = True, type=str)

    def handle(self, *args, **options):

        try:
            cv = Cv.objects.get(name=options['name'],definition=options['definition'])

            self.stdout.write('Deleting %s %s and every child record (CASCADE)' % (options['name'],options['definition']))

            cvterm_ids = Cvterm.objects.filter(cv=cv).values_list('cvterm_id', flat=True)
            dbxref_ids = CvtermDbxref.objects.filter(cvterm_id__in=cvterm_ids).values_list('dbxref_id', flat=True)
            Dbxref.objects.filter(dbxref_id__in=dbxref_ids).delete()

            dbxref_ids = Cvterm.objects.filter(cv=cv).values_list('dbxref_id', flat=True)
            Dbxref.objects.filter(dbxref_id__in=dbxref_ids).delete()

            cv.delete()

            self.stdout.write(self.style.SUCCESS('Done'))
        except ObjectDoesNotExist:
            self.stdout.write(self.style.ERROR('Cannot remove %s %s (not registered)' % (options['name'],options['definition'])))

