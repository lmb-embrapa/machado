from django.core.management.base import BaseCommand, CommandError
from chado.models import Cv,Cvterm,CvtermDbxref,Dbxref,Db

class Command(BaseCommand):
    help = 'Remove Sequence Ontology (CASCADE)'

    def add_arguments(self, parser):
        parser.add_argument("--name", help="cv.name", required = True, type=str)
        parser.add_argument("--definition", help="cv.definition", required = True, type=str)


    def handle(self, *args, **options):

        if Cv.objects.get(name=options['name'],definition=options['definition']):
            cv = Cv.objects.get(name=options['name'],definition=options['definition'])
            for cvterm in Cvterm.objects.filter(cv=cv):
                Dbxref.objects.filter(dbxref_id=cvterm.dbxref_id).delete()
            cv.delete()

            cv = Cv.objects.get(name='cvterm_relationship',definition=options['definition'])
            for cvterm in Cvterm.objects.filter(cv=cv):
                Dbxref.objects.filter(dbxref_id=cvterm.dbxref_id).delete()
            cv.delete()

            cv = Cv.objects.get(name='cvterm_property_type',definition=options['definition'])
            for cvterm in Cvterm.objects.filter(cv=cv):
                Dbxref.objects.filter(dbxref_id=cvterm.dbxref_id).delete()
            cv.delete()

            cv = Cv.objects.get(name='synonym_type',definition=options['definition'])
            for cvterm in Cvterm.objects.filter(cv=cv):
                Dbxref.objects.filter(dbxref_id=cvterm.dbxref_id).delete()
            cv.delete()


