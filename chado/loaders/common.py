"""loaders common library."""
from chado.loaders.exceptions import ImportingError
from chado.models import Cv, Cvterm, CvtermDbxref, Cvtermsynonym
from chado.models import Db, Dbxref, Organism
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
import os
import re


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


class Ontology(object):
    """Ontology preprocessing."""

    def __init__(self, cv_name, cv_definition=''):
        """Invoke all validations."""
        # Save the name and definition to the Cv model
        try:
            # Check if the so file is already loaded
            cv = Cv.objects.get(name=cv_name)

            if cv is not None:
                raise ImportingError(
                    'Cv -> cannot load {} (already registered)'.format(
                        cv_name))

        except ObjectDoesNotExist:
            self.cv = Cv.objects.create(name=cv_name,
                                        definition=cv_definition)
            self.cv.save()

        # Creating db _global
        self.db_global, created = Db.objects.get_or_create(name='_global')
        # Creating db internal
        self.db_internal, created = Db.objects.get_or_create(name='internal')
        # Creating db obo_rel
        self.db_obo_rel, created = Db.objects.get_or_create(name='obo_rel')

        # Creating cv cvterm_property_type
        self.cv_cvterm_property_type, created = Cv.objects.get_or_create(
            name='cvterm_property_type')
        # Creating cv relationshipo
        self.cv_relationship, created = Cv.objects.get_or_create(
            name='relationship')
        # Creating cv relationship
        self.cv_synonym_type, created = Cv.objects.get_or_create(
            name='synonym_type')
        # Creating cv sequence
        self.cv_sequence, created = Cv.objects.get_or_create(
            name='sequence')

        # Creating dbxref and cvterm is_symmetric
        self.dbxref_is_symmetric, created = Dbxref.objects.get_or_create(
            db=self.db_internal, accession='is_symmetric')
        self.cvterm_is_symmetric, created = Cvterm.objects.get_or_create(
                cv=self.cv_cvterm_property_type,
                name='is_symmetric',
                definition='',
                dbxref=self.dbxref_is_symmetric,
                is_obsolete=0,
                is_relationshiptype=0)

        # Creating dbxref and cvterm is_anti_symmetric
        self.dbxref_is_anti_symmetric, created = Dbxref.objects.get_or_create(
            db=self.db_internal, accession='is_anti_symmetric')
        self.cvterm_is_anti_symmetric, created = Cvterm.objects.get_or_create(
                cv=self.cv_cvterm_property_type,
                name='is_anti_symmetric',
                definition='',
                dbxref=self.dbxref_is_anti_symmetric,
                is_obsolete=0,
                is_relationshiptype=0)

        # Creating dbxref and cvterm is_transitive
        dbxref_is_transitive, created = Dbxref.objects.get_or_create(
            db=self.db_internal, accession='is_transitive')
        self.cvterm_is_transitive, created = Cvterm.objects.get_or_create(
                cv=self.cv_cvterm_property_type,
                name='is_transitive',
                definition='',
                dbxref=dbxref_is_transitive,
                is_obsolete=0,
                is_relationshiptype=0)

        # Creating dbxref and cvterm is_reflexive
        dbxref_is_reflexive, created = Dbxref.objects.get_or_create(
            db=self.db_internal, accession='is_reflexive')
        self.cvterm_is_reflexive, created = Cvterm.objects.get_or_create(
                cv=self.cv_cvterm_property_type,
                name='is_reflexive',
                definition='',
                dbxref=dbxref_is_reflexive,
                is_obsolete=0,
                is_relationshiptype=0)

        # Creating dbxref and cvterm is_class_level
        dbxref_is_class_level, created = Dbxref.objects.get_or_create(
            db=self.db_internal, accession='is_class_level')
        self.cvterm_is_class_level, created = Cvterm.objects.get_or_create(
                cv=self.cv_cvterm_property_type,
                name='is_class_level',
                definition='',
                dbxref=dbxref_is_class_level,
                is_obsolete=0,
                is_relationshiptype=0)

        # Creating dbxref and cvterm is_metadata_tag
        dbxref_is_metadata_tag, created = Dbxref.objects.get_or_create(
            db=self.db_internal, accession='is_metadata_tag')
        self.cvterm_is_metadata_tag, created = Cvterm.objects.get_or_create(
                cv=self.cv_cvterm_property_type,
                name='is_metadata_tag',
                definition='',
                dbxref=dbxref_is_metadata_tag,
                is_obsolete=0,
                is_relationshiptype=0)

        # Creating dbxref and cvterm comment
        dbxref_comment, created = Dbxref.objects.get_or_create(
            db=self.db_internal, accession='comment')
        self.cvterm_comment, created = Cvterm.objects.get_or_create(
            cv=self.cv_cvterm_property_type,
            name='comment',
            definition='',
            dbxref=dbxref_comment,
            is_obsolete=0,
            is_relationshiptype=0)

        # Creating dbxref and cvterm is_a
        dbxref_is_a, created = Dbxref.objects.get_or_create(
            db=self.db_obo_rel, accession='is_a')
        self.cvterm_is_a, created = Cvterm.objects.get_or_create(
            cv=self.cv_relationship,
            name='is_a',
            definition='',
            dbxref=dbxref_is_a,
            is_obsolete=0,
            is_relationshiptype=1)


def process_cvterm_def(cvterm, definition):
    """Process defition to obtain cvterms."""
    text = ''

    '''
    Definition format:
    "text" [refdb:refcontent, refdb:refcontent]

    Definition format example:
    "A gene encoding an mRNA that has the stop codon redefined as
     pyrrolysine." [SO:xp]
    '''
    if definition:

        # Retrieve text and dbxrefs
        try:
            text, dbxrefs = definition.split('" [')
            text = re.sub(r'^"', '', text)
            dbxrefs = re.sub(r'\]$', '', dbxrefs)
        except ValueError:
            text = definition
            dbxrefs = ''

        if dbxrefs:

            dbxrefs = dbxrefs.split(', ')

            # Save all dbxrefs
            for dbxref in dbxrefs:
                ref_db, ref_content = dbxref.split(':', 1)

                if ref_db == 'http':
                    ref_db = 'URL'
                    ref_content = 'http:'+ref_content

                # Get/Set Dbxref instance: ref_db,ref_content
                db, created = Db.objects.get_or_create(name=ref_db)
                dbxref, created = Dbxref.objects.get_or_create(
                    db=db, accession=ref_content)

                # Estabilish the cvterm and the dbxref relationship
                CvtermDbxref.objects.get_or_create(cvterm=cvterm,
                                                   dbxref=dbxref,
                                                   is_for_definition=1)

    cvterm.definition = text
    cvterm.save()
    return


def process_cvterm_xref(cvterm, xref, is_for_definition=0):
    """Process cvterm_xref."""
    if xref:

        ref_db, ref_content = xref.split(':', 1)

        if ref_db == 'http':
            ref_db = 'URL'
            ref_content = 'http:'+ref_content

        # Get/Set Dbxref instance: ref_db,ref_content
        db, created = Db.objects.get_or_create(name=ref_db)
        dbxref, created = Dbxref.objects.get_or_create(
            db=db, accession=ref_content)

        # Estabilish the cvterm and the dbxref relationship
        CvtermDbxref.objects.get_or_create(cvterm=cvterm,
                                           dbxref=dbxref,
                                           is_for_definition=is_for_definition)
    return


def process_cvterm_go_synonym(cvterm, synonym, synonym_type):
    """Process cvterm_go_synonym.

    Definition format:
    "text" [refdb:refcontent, refdb:refcontent]

    Definition format example:
    "30S ribosomal subunit assembly" [GOC:mah]
    """
    # Retrieve text and dbxrefs
    text, dbxrefs = synonym.split('" [')
    synonym_text = re.sub(r'^"', '', text)
    synonym_type = re.sub(r'_synonym', '', synonym_type).lower()

    # Handling the synonym_type
    db_type, created = Db.objects.get_or_create(name='internal')
    dbxref_type, created = Dbxref.objects.get_or_create(
        db=db_type, accession=synonym_type)

    cv_synonym_type, created = Cv.objects.get_or_create(name='synonym_type')
    cvterm_type, created = Cvterm.objects.get_or_create(
        cv=cv_synonym_type,
        name=synonym_type,
        definition='',
        dbxref=dbxref_type,
        is_obsolete=0,
        is_relationshiptype=0)

    # Storing the synonym
    try:
        cvtermsynonym = Cvtermsynonym.objects.create(
            cvterm=cvterm,
            synonym=synonym_text,
            type_id=cvterm_type.cvterm_id)
        cvtermsynonym.save()
    # Ignore if already created
    except IntegrityError:
        pass

    return


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
