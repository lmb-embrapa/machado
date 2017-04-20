from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from chado.models import Organism


class Command(BaseCommand):
    help = 'Insert organism'

    def add_arguments(self, parser):
        parser.add_argument("--abbreviation", help="abbreviation",
                            required=False, type=str)
        parser.add_argument("--genus", help="genus", required=True,
                            type=str)
        parser.add_argument("--species", help="species", required=True,
                            type=str)
        parser.add_argument("--common_name", help="common name",
                            required=False, type=str)
        parser.add_argument("--infraspecific_name", help="infraspecific name",
                            required=False, type=str)
        parser.add_argument("--type", help="type (Organism_type_Cvterm)",
                            required=False, type=str)
        parser.add_argument("--comment", help="comment", required=False,
                            type=str)

    def handle(self, *args, **options):

        species = options['species']
        genus = options['genus']

        try:
            spp = Organism.objects.get(species=species, genus=genus)

            if (spp is not None):
                raise IntegrityError('Organism already registered!')
        except ObjectDoesNotExist:
            organism = Organism.objects.create(
                abbreviation=options['abbreviation'],
                genus=options['genus'],
                species=options['species'],
                common_name=options['common_name'],
                infraspecific_name=options['infraspecific_name'],
                type=options['type'],
                comment=options['comment'])
            organism.save()
            self.stdout.write(self.style.SUCCESS('%s registered' % species))
