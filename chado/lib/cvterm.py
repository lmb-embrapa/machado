"""cvterm library."""
from cachetools import cached
from chado.models import Cv, Cvterm, CvtermDbxref, Cvtermprop, Cvtermsynonym
from chado.lib.dbxref import get_set_dbxref
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
import re


@cached(cache={})
def get_set_cv(cv_name, **args):
    """Create/Retrieve cv object.

    It tries to get the cv object or create it otherwise.

    Args:
        cv_name: type string

    Returns:
        cv: type object

    """
    try:
        # Check if the cv is already registered
        cv = Cv.objects.get(name=cv_name)
        return cv

    except ObjectDoesNotExist:

        # Save the name to the Db model
        cv = Cv.objects.create(name=cv_name,
                               definition=args.get('definition'))
        cv.save()
        return cv


@cached(cache={})
def get_set_cvterm(cv_name, cvterm_name, dbxref, **kargs):
    """Create/Retrieve cvterm object."""
    definition = kargs.get('definition')
    is_relationshiptype = kargs.get('is_relationshiptype')
    """
    It tries to get the cvterm object or create it otherwise.

    Note:
        This functions invokes get_set_cv in order
        to retrieve a cv object

    Args:
        cv_name: type string
        cvterm_name: type string
        dbxref: type object

    kargs (optional):
        definition: type string
        is_relationshiptype: type boolean

    Returns:
        cvterm: type object
    """

    # Get/Set Cv instance: cv
    cv = get_set_cv(cv_name)

    try:
        # Check if the cvterm is already registered
        cvterm = Cvterm.objects.get(cv=cv, name=cvterm_name)
        return cvterm

    except ObjectDoesNotExist:
        if (not is_relationshiptype):
            is_relationshiptype = 0

        # Save the name to the Cvterm model
        cvterm = Cvterm.objects.create(cv=cv,
                                       name=cvterm_name,
                                       definition=definition,
                                       dbxref=dbxref,
                                       is_obsolete=0,
                                       is_relationshiptype=is_relationshiptype)
        cvterm.save()
        return cvterm


@cached(cache={})
def get_set_cvtermprop(cvterm, type_id, value, rank):
    """Create/Retrieve cvtermprop object."""
    try:
        # Check if the cvtermprop is already registered
        cvtermprop = Cvtermprop.objects.get(cvterm=cvterm,
                                            type_id=type_id,
                                            value=value,
                                            rank=rank)
        return cvterm

    except ObjectDoesNotExist:

        # Save the name to the Cvtermprop model
        cvtermprop = Cvtermprop.objects.create(cvterm=cvterm,
                                               type_id=type_id,
                                               value=value,
                                               rank=rank)
        cvtermprop.save()
        return cvtermprop


@cached(cache={})
def get_set_cvterm_dbxref(cvterm, dbxref, is_for_definition):
    """Create/Retrieve cvterm_dbxref object."""
    try:
        # Check if the dbxref is already registered
        cvtermdbxref = CvtermDbxref.objects.get(cvterm=cvterm, dbxref=dbxref)
        return cvtermdbxref

    except ObjectDoesNotExist:

        # Save to the Dbxref model
        cvtermdbxref = CvtermDbxref.objects.create(
            cvterm=cvterm,
            dbxref=dbxref,
            is_for_definition=is_for_definition)
        cvtermdbxref.save()
        return cvtermdbxref


def process_cvterm_def(cvterm, definition):
    """Process defition to obtain cvterms."""
    text = ''

    '''
    Definition format:
    "text" [refdb:refcontent, refdb:refcontent]

    Definition format example:
    "A gene encoding an mRNA that has the stop codon redefined as
    # pyrrolysine." [SO:xp]
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
                dbxref = get_set_dbxref(ref_db, ref_content)

                # Estabilish the cvterm and the dbxref relationship
                get_set_cvterm_dbxref(cvterm, dbxref, 1)

    cvterm.definition = text
    cvterm.save()
    return


def process_cvterm_xref(cvterm, xref):
    """Process cvterm_xref."""
    if xref:

        ref_db, ref_content = xref.split(':', 1)

        if ref_db == 'http':
            ref_db = 'URL'
            ref_content = 'http:'+ref_content

        # Get/Set Dbxref instance: ref_db,ref_content
        dbxref = get_set_dbxref(ref_db, ref_content)

        # Estabilish the cvterm and the dbxref relationship
        get_set_cvterm_dbxref(cvterm, dbxref, 0)
    return


def process_cvterm_so_synonym(cvterm, synonym):
    """Process cvterm_so_synonym.

    Definition format:
    "text" cvterm []

    Definition format example:
    "stop codon gained" EXACT []

    Attention:
    There are several cases that don't follow this format.
    These are being ignored for now.
    """
    pattern = re.compile(r'^"(.+)" (\w+) \[\]$')
    matches = pattern.findall(synonym)

    if len(matches) != 1 or len(matches[0]) != 2:
        return

    synonym_text, synonym_type = matches[0]

    # Handling the synonym_type
    dbxref_type = get_set_dbxref('internal',
                                 synonym_type.lower())
    cvterm_type = get_set_cvterm(cv_name='synonym_type',
                                 cvterm_name=synonym_type.lower(),
                                 definition='',
                                 dbxref=dbxref_type,
                                 is_relationshiptype=0)

    # Storing the synonym
    cvtermsynonym = Cvtermsynonym.objects.create(cvterm=cvterm,
                                                 synonym=synonym_text,
                                                 type_id=cvterm_type.cvterm_id)
    cvtermsynonym.save()
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
    dbxref_type = get_set_dbxref('internal', synonym_type)
    cvterm_type = get_set_cvterm(cv_name='synonym_type',
                                 cvterm_name=synonym_type,
                                 definition='',
                                 dbxref=dbxref_type,
                                 is_relationshiptype=0)

    # Storing the synonym
    #
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


@cached(cache={})
def get_ontology_term(ontology, term):
    """Retrieve ontology term."""
    # Retrieve sequence ontology object
    try:
        cv = Cv.objects.get(name=ontology)
    except ObjectDoesNotExist:
        raise ObjectDoesNotExist('Sequence Ontology not loaded (%s).'
                                 % (ontology))

    # Retrieve sequence ontology term object
    try:
        cvterm = Cvterm.objects.get(cv=cv, name=term)
    except ObjectDoesNotExist:
        raise ObjectDoesNotExist('Sequence Ontology term not found (%s).'
                                 % (term))
    return cvterm


@cached(cache={})
def get_cvterm(cv_name, cvterm_name, **kargs):
    """Retrieve cvterm object."""
    # Get/Set Cv instance: cv
    cv = get_set_cv(cv_name)

    try:
        # Check if the cvterm is already registered
        cvterm = Cvterm.objects.get(cv=cv, name=cvterm_name)
        return cvterm
    except ObjectDoesNotExist:
        return None
