"""loaders common library."""
from chado.loaders.exceptions import ImportingError
from chado.models import Cv, Cvterm
from chado.models import Organism
from django.core.exceptions import ObjectDoesNotExist
import os


class Validator(object):
    """Validate input file."""

    def validate(self, file_path):
        """Invoke all validations."""
        self._exists(file_path)
        self._is_file(file_path)
        self._is_readable(file_path)

    def _exists(self, file_path):
        """Check whether a file exists."""
        if not os.path.exists(file_path):
            raise ImportingError("{} does not exist".format(file_path))

    def _is_file(self, file_path):
        """Check whether file is actually a file type."""
        if not os.path.isfile(file_path):
            raise ImportingError("{} is not a file".format(file_path))

    def _is_readable(self, file_path):
        """Check file is readable."""
        try:
            f = open(file_path, 'r')
            f.close()
        except IOError:
            raise ImportingError("{} is not readable".format(file_path))


def get_ontology_term(ontology, term):
    """Retrieve ontology term."""
    # Retrieve sequence ontology object
    try:
        cv = Cv.objects.get(name=ontology)
    except ObjectDoesNotExist:
        raise ObjectDoesNotExist(
            'Sequence Ontology not loaded ({}).'.format(ontology))

    # Retrieve sequence ontology term object
    try:
        cvterm = Cvterm.objects.get(cv=cv, name=term)
    except ObjectDoesNotExist:
        raise ObjectDoesNotExist(
            'Sequence Ontology term not found ({}).'.format(term))
    return cvterm


def insert_organism(genus, species, *args, **options):
    """Insert organism."""
    if species is None or genus is None:
        raise ImportingError('species and genus are required!')

    type_id = ''
    if options.get('type') is not None:
        try:
            cvterm = Cvterm.objects.get(name=options.get('type'))
            type_id = cvterm.cvterm_id
        except ObjectDoesNotExist:
            raise ImportingError(
                'The type must be previously registered in Cvterm')

    try:
        spp = Organism.objects.get(genus=genus, species=species)
        if (spp is not None):
            raise ImportingError('Organism already registered ({} {})!'
                                 .format(genus, species))
    except ObjectDoesNotExist:
        organism = Organism.objects.create(
            abbreviation=options.get('abbreviation'),
            genus=genus,
            species=species,
            common_name=options.get('common_name'),
            infraspecific_name=options.get('infraspecific_name'),
            type_id=type_id,
            comment=options.get('comment'))
        organism.save()
