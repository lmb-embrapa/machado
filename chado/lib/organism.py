from django.core.exceptions import ObjectDoesNotExist
from chado.models import Organism


def get_organism(organism):

    try:
        genus, species = organism.split(' ')
    except ValueError:
        raise ValueError('The organism genus and species should be '
                         'separated by a single space')

    try:
        organism = Organism.objects.get(species=species, genus=genus)
    except ObjectDoesNotExist:
        raise ObjectDoesNotExist('%s not registered.'
                                 % organism)
    return organism
