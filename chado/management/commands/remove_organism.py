from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from chado.models import Organism


class Command(BaseCommand):
    help = 'Remove organism'

    def add_arguments(self, parser):
        parser.add_argument("--genus",
                            help="genus",
                            required=True,
                            type=str)
        parser.add_argument("--species",
                            help="species",
                            required=True,
                            type=str)

    def handle(self, *args, **options):

        species = options['species']
        genus = options['genus']

        try:
            organism = Organism.objects.get(species=species, genus=genus)
            if organism:
                organism.delete()
                self.stdout.write(self.style.SUCCESS('%s %s removed'
                                                     % (genus, species)))

        except ObjectDoesNotExist:
                print('Organism does not exist in database!')
