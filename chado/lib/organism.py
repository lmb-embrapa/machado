from django.core.exceptions import ObjectDoesNotExist
from chado.models import Organism, OrganismDbxref


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


def get_set_organism(organism_name, infra_name=""):
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
    return (organism)


def get_set_organism_dbxref(organism, dbxref):
    organism_dbxref = ""
    # receives an organism binomial name with "Genus species" format
    try:
        organism_dbxref = OrganismDbxref.objects.get(organism=organism,
                                                     dbxref=dbxref)
    except ObjectDoesNotExist:
        organism_dbxref = OrganismDbxref.objects.create(organism=organism,
                                                        dbxref=dbxref)
    return (organism_dbxref)
