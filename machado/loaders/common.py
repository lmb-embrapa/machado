# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""loaders common library."""
from machado.loaders.exceptions import ImportingError
from django.db.utils import IntegrityError
from machado.models import Cv, Cvterm
from machado.models import Organism
from machado.models import Feature
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
import os


class FileValidator(object):
    """Validate input file."""

    def validate(self, file_path: str) -> None:
        """Invoke all validations."""
        self._exists(file_path)
        self._is_file(file_path)
        self._is_readable(file_path)

    def _exists(self, file_path: str) -> None:
        """Check whether a file exists."""
        if not os.path.exists(file_path):
            raise ImportingError("{} does not exist".format(file_path))

    def _is_file(self, file_path: str) -> None:
        """Check whether file is actually a file type."""
        if not os.path.isfile(file_path):
            raise ImportingError("{} is not a file".format(file_path))

    def _is_readable(self, file_path: str) -> None:
        """Check file is readable."""
        try:
            f = open(file_path, 'r')
            f.close()
        except IOError:
            raise ImportingError("{} is not readable".format(file_path))


class FieldsValidator(object):
    """Validate fields from tabular or .csv file."""

    def validate(self, nfields: int, fields: list) -> None:
        """Invoke all validations."""
        self._nfields(nfields, fields)
        self._nullfields(fields)

    def _nfields(self, nfields: int, fields: list) -> None:
        """Check if number of fields are correct."""
        if len(fields) != nfields:
            raise ImportingError("Provided number of fields {} differ from {}"
                                 .format(nfields, len(fields)))

    def _nullfields(self, fields: list) -> None:
        counter = 0
        for field in fields:
            if (field is None or field == ""):
                raise ImportingError("Found null or empty field in position {}"
                                     .format(counter))
            counter += 1


def retrieve_ontology_term(ontology: str, term: str) -> Cvterm:
    """Retrieve ontology term."""
    # Retrieve sequence ontology object
    try:
        cv = Cv.objects.get(name=ontology)
    except ObjectDoesNotExist:
        raise ObjectDoesNotExist(
            'Ontology not loaded ({}).'.format(ontology))

    # Retrieve sequence ontology term object
    try:
        cvterm = Cvterm.objects.get(cv=cv, name=term)
    except ObjectDoesNotExist:
        raise ObjectDoesNotExist(
            'Ontology term not found ({}).'.format(term))
    return cvterm


def insert_organism(genus: str,
                    species: str = 'spp.',
                    type: str = None,
                    infraspecific_name: str = None,
                    abbreviation: str = None,
                    common_name: str = None,
                    comment: str = None) -> None:
    """Insert organism."""
    if genus is None:
        raise ImportingError('genus is required!')

    type_id = ''
    if type is not None:
        try:
            cvterm = Cvterm.objects.get(name=type)
            type_id = cvterm.cvterm_id
        except ObjectDoesNotExist:
            raise ImportingError(
                'The type must be previously registered in Cvterm')

    try:
        spp = Organism.objects.get(
            genus=genus, species=species,
            infraspecific_name=infraspecific_name)
        if (spp is not None):
            raise ImportingError('Organism already registered ({} {})!'
                                 .format(genus, species))
    except ObjectDoesNotExist:
        organism = Organism.objects.create(
            abbreviation=abbreviation,
            genus=genus,
            species=species,
            common_name=common_name,
            infraspecific_name=infraspecific_name,
            type_id=type_id,
            comment=comment)
        organism.save()


def retrieve_organism(organism: str) -> Organism:
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
        raise ObjectDoesNotExist('{} not registered.'.format(organism))
    return organism


def retrieve_feature(featureacc: str,
                     organism: Organism = None,
                     cvterm: str = "mRNA",
                     ontology: str = "sequence",
                     ) -> Feature:
    """Retrieve feature object. Expects feature source to be 'GFF_SOURCE'."""
    # cvterm is mandatory
    try:
        cvterm = retrieve_ontology_term(ontology=ontology,
                                        term=cvterm)
    except ObjectDoesNotExist as e:
        raise ImportingError(e)
    try:
        feature = Feature.objects.get(uniquename=featureacc,
                                      type_id=cvterm.cvterm_id)
    except MultipleObjectsReturned:
        feature = Feature.objects.get(uniquename=featureacc,
                                      type_id=cvterm.cvterm_id,
                                      organism=organism)
    # this will make the function return ObjectDoesNotExist!
    except ObjectDoesNotExist:
        feature = None
    except IntegrityError as e:
        raise ImportingError(e)
    return feature
