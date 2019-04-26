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
import gzip
import os

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

from machado.loaders.exceptions import ImportingError
from machado.models import Feature, FeatureDbxref, Organism


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
            f = open(file_path, "r")
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
            raise ImportingError(
                "Provided number of fields {} differ from {}".format(
                    nfields, len(fields)
                )
            )

    def _nullfields(self, fields: list) -> None:
        counter = 0
        for field in fields:
            if field is None or field == "":
                raise ImportingError(
                    "Found null or empty field in position {}".format(counter)
                )
            counter += 1


def get_num_lines(file_path):
    """Count number of lines in a text file."""
    if file_path.endswith(".gz"):
        fp = gzip.open(file_path, "r+")
    else:
        fp = open(file_path, "r+")

    i = 0
    for line in fp:
        if str(line).startswith("#"):
            continue
        i += 1
    return i


def insert_organism(
    genus: str,
    species: str = "spp.",
    infraspecific_name: str = None,
    abbreviation: str = None,
    common_name: str = None,
    comment: str = None,
) -> None:
    """Insert organism."""
    try:
        spp = Organism.objects.get(
            genus=genus, species=species, infraspecific_name=infraspecific_name
        )
        if spp is not None:
            raise ImportingError(
                "Organism already registered ({} {})!".format(genus, species)
            )
    except ObjectDoesNotExist:
        organism = Organism.objects.create(
            abbreviation=abbreviation,
            genus=genus,
            species=species,
            common_name=common_name,
            infraspecific_name=infraspecific_name,
            comment=comment,
        )
        organism.save()


def retrieve_organism(organism: str) -> Organism:
    """Retrieve organism object."""
    try:
        aux = organism.split(" ")
        genus = aux[0]
        species = "spp."
        infraspecific_name = None
        if len(aux) == 2:
            species = aux[1]
        elif len(aux) > 2:
            species = aux[1]
            infraspecific_name = " ".join(aux[2:])
    except ValueError:
        raise ValueError(
            "The organism genus and species should be " "separated by a single space"
        )
    except AttributeError as e:
        raise AttributeError(e)

    try:
        organism_obj = Organism.objects.get(
            genus=genus, species=species, infraspecific_name=infraspecific_name
        )
    except ObjectDoesNotExist:
        raise ObjectDoesNotExist("{} not registered.".format(organism))
    return organism_obj


def retrieve_feature_id(accession: str, soterm: str) -> int:
    """Retrieve feature object."""
    # feature.uniquename
    try:
        return Feature.objects.get(
            uniquename=accession, type__cv__name="sequence", type__name=soterm
        ).feature_id
    except (MultipleObjectsReturned, ObjectDoesNotExist):
        pass

    # feature.dbxref.accession
    try:
        return Feature.objects.get(
            dbxref__accession=accession, type__cv__name="sequence", type__name=soterm
        ).feature_id
    except (MultipleObjectsReturned, ObjectDoesNotExist):
        pass

    # featuredbxref.dbxref.accession
    return FeatureDbxref.objects.get(
        dbxref__accession=accession,
        feature__type__cv__name="sequence",
        feature__type__name=soterm,
    ).feature_id
