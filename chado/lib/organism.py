"""organism library."""
from django.core.exceptions import ObjectDoesNotExist
from chado.models import Organism


def get_organism(organism):
    """Retrieve organism object."""
    try:
        aux = organism.split(' ')
        genus = aux[0]
        species = 'spp.'
        infraspecific = None
        if len(aux) == 2:
            species = aux[1]
        elif len(aux) > 2:
            species = aux[1]
            infraspecific = ' '.join(aux[2:])

    except ValueError:
        raise ValueError('The organism genus and species should be '
                         'separated by a single space')

    try:
        organism = Organism.objects.get(species=species,
                                        genus=genus,
                                        infraspecific_name=infraspecific)
    except ObjectDoesNotExist:
        raise ObjectDoesNotExist('%s not registered.'
                                 % organism)
    return organism


def get_set_organism(organism_name, infra_name=""):
    """Create/Retrieve organism object."""
    # receives an organism binomial name with "Genus species" format
    genus = ""
    species = ""
    organism = ""
    try:
        genus, species = organism_name.split(' ')
    except ValueError:
        raise ValueError('The organism genus and species should be '
                         'separated by a single space')

    try:
        organism = Organism.objects.get(species=species, genus=genus,
                                        infraspecific_name=infra_name)
    except ObjectDoesNotExist:
        organism = Organism.objects.create(genus=genus, species=species,
                                           infraspecific_name=infra_name)
    return organism
