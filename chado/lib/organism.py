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


def get_set_organism(organism_name):
    # receives an organism binomial name with "Genus species" format
    genus = ""
    species = ""
    try:
        genus, species = organism_name.split(' ')
    except ValueError:
        raise ValueError('The organism genus and species should be '
                         'separated by a single space')

    try:
        organism = Organism.objects.get(species=species, genus=genus)
    except ObjectDoesNotExist:
        organism = Organism.objects.create(genus=genus, species=species)
        organism.save()
    return (organism)
