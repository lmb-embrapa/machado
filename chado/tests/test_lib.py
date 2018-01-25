"""Tests Libraries."""

from chado.lib.cvterm import get_cvterm, get_set_cv, get_set_cvterm
from chado.lib.cvterm import get_set_cvterm_dbxref, get_set_cvtermprop
from chado.lib.cvterm import get_ontology_term
from chado.lib.cvterm import process_cvterm_def, process_cvterm_xref
from chado.lib.db import get_set_db, get_set_dbprop, set_db_file
from chado.lib.dbxref import get_set_dbxref, get_dbxref
from chado.models import Cv, Cvterm, CvtermDbxref, Cvtermprop
from chado.models import Db, Dbprop, Dbxref
from django.test import TestCase


class DbLibTest(TestCase):
    """Tests Libraries - DB."""

    def test_get_set_db_new(self):
        """Tests - get_set_db - new."""
        test_db = get_set_db(db_name='test_db_name_new',
                             description='test_db_description',
                             urlprefix='test_db_urlprefix',
                             url='test_db_url')
        self.assertEqual('test_db_name_new', test_db.name)
        self.assertEqual('test_db_description', test_db.description)
        self.assertEqual('test_db_urlprefix', test_db.urlprefix)
        self.assertEqual('test_db_url', test_db.url)

    def test_get_set_db_existing(self):
        """Tests - get_set_db - existing."""
        Db.objects.create(name='test_db_name_existing',
                          description='test_db_description',
                          urlprefix='test_db_urlprefix',
                          url='test_db_url')

        test_db = get_set_db(db_name='test_db_name_existing')

        self.assertEqual('test_db_name_existing', test_db.name)
        self.assertEqual('test_db_description', test_db.description)
        self.assertEqual('test_db_urlprefix', test_db.urlprefix)
        self.assertEqual('test_db_url', test_db.url)

    def test_set_db_file(self):
        """Tests - set_db_file."""
        test_db = set_db_file(file='/tmp/test_name.file')
        self.assertEqual('test_name.file', test_db.name)

    def test_get_set_dbprop_new(self):
        """Tests - get_set_dbprop."""
        test_db = set_db_file(file='/tmp/test_dbprop_new.file')

        test_dbxref = get_set_dbxref(db_name='test_db_name_new',
                                     accession='test_db_accession_new',
                                     description='test_db_description',
                                     version='test_db_version')

        test_cvterm = get_set_cvterm(cv_name='test_db_name_new',
                                     cvterm_name='test_db_name_new',
                                     dbxref=test_dbxref,
                                     definition='test_db_definition',
                                     is_relationshiptype=1)

        test_dbprop = get_set_dbprop(db=test_db,
                                     type_id=test_cvterm.cvterm_id,
                                     value='test_db_value_new',
                                     rank=1)

        self.assertEqual('test_db_value_new', test_dbprop.value)
        self.assertEqual(1, test_dbprop.rank)

    def test_get_set_dbprop_existing(self):
        """Tests - get_set_dbprop."""
        test_db = set_db_file(file='/tmp/test_dbprop_existing.file')

        test_dbxref = get_set_dbxref(db_name='test_db_name_existing',
                                     accession='test_db_accession_new',
                                     description='test_db_description',
                                     version='test_db_version')

        test_cvterm = get_set_cvterm(cv_name='test_db_name_existing',
                                     cvterm_name='test_db_name_existing',
                                     dbxref=test_dbxref,
                                     definition='test_db_definition',
                                     is_relationshiptype=1)

        Dbprop.objects.create(db=test_db,
                              type_id=test_cvterm.cvterm_id,
                              value='test_db_value_existing',
                              rank=1)

        test_dbprop = get_set_dbprop(db=test_db,
                                     type_id=test_cvterm.cvterm_id)

        self.assertEqual('test_db_value_existing', test_dbprop.value)
        self.assertEqual(1, test_dbprop.rank)


class DbxrefLibTest(TestCase):
    """Tests Libraries - DBxref."""

    def test_get_set_dbxref_new(self):
        """Tests - get_set_dbxref - new."""
        test_dbxref = get_set_dbxref(db_name='test_dbxref_name_new',
                                     accession='test_dbxref_accession_new',
                                     description='test_dbxref_description',
                                     version='test_dbxref_version')
        self.assertEqual('test_dbxref_accession_new', test_dbxref.accession)
        self.assertEqual('test_dbxref_description', test_dbxref.description)
        self.assertEqual('test_dbxref_version', test_dbxref.version)

    def test_get_set_dbxref_existing(self):
        """Tests - get_set_dbxref - existing."""
        test_db = Db.objects.create(name='test_dbxref_name_existing',
                                    description='test_dbxref_description',
                                    urlprefix='test_dbxref_urlprefix',
                                    url='test_dbxref_url')
        Dbxref.objects.create(db=test_db,
                              accession='test_dbxref_accession_existing',
                              description='test_dbxref_description',
                              version='test_dbxref_version')

        test_dbxref = get_set_dbxref(
            db_name='test_dbxref_name_existing',
            accession='test_dbxref_accession_existing')

        self.assertEqual('test_dbxref_accession_existing',
                         test_dbxref.accession)
        self.assertEqual('test_dbxref_description', test_dbxref.description)
        self.assertEqual('test_dbxref_version', test_dbxref.version)

    def test_get_dbxref(self):
        """Tests - get_dbxref."""
        db_test = Db.objects.create(name='test_dbxref_name',
                                    description='test_dbxref_description',
                                    urlprefix='test_dbxref_urlprefix',
                                    url='test_dbxref_url')
        Dbxref.objects.create(db=db_test,
                              accession='test_dbxref_accession',
                              description='test_dbxref_description',
                              version='test_dbxref_version')

        test_dbxref = get_dbxref(db_name='test_dbxref_name',
                                 accession='test_dbxref_accession')
        self.assertEqual('test_dbxref_accession', test_dbxref.accession)
        self.assertEqual('test_dbxref_description', test_dbxref.description)
        self.assertEqual('test_dbxref_version', test_dbxref.version)


class CvtermLibTest(TestCase):
    """Tests Libraries - Cvterm."""

    def test_get_set_cv_new(self):
        """Tests - get_set_cv - new."""
        test_cv = get_set_cv(cv_name='test_cvterm_name_new',
                             definition='test_cvterm_definition')

        self.assertEqual('test_cvterm_name_new', test_cv.name)
        self.assertEqual('test_cvterm_definition', test_cv.definition)

    def test_get_set_cv_existing(self):
        """Tests - get_set_cv - existing."""
        Cv.objects.create(name='test_cvterm_name_existing',
                          definition='test_cvterm_definition')

        test_cv = get_set_cv(cv_name='test_cvterm_name_existing')

        self.assertEqual('test_cvterm_name_existing', test_cv.name)
        self.assertEqual('test_cvterm_definition', test_cv.definition)

    def test_get_cvterm(self):
        """Tests - get_cvterm."""
        test_dbxref = get_set_dbxref(
            db_name='test_cvterm_name',
            accession='test_cvterm_accession',
            description='test_cvterm_description',
            version='test_cvterm_version')

        get_set_cvterm(cv_name='test_cvterm_name',
                       cvterm_name='test_cvterm_name',
                       dbxref=test_dbxref,
                       definition='test_cvterm_definition',
                       is_relationshiptype=1)

        test_cvterm = get_cvterm(cv_name='test_cvterm_name',
                                 cvterm_name='test_cvterm_name')

        self.assertEqual('test_cvterm_name', test_cvterm.name)
        self.assertEqual('test_cvterm_definition', test_cvterm.definition)
        self.assertEqual(0, test_cvterm.is_obsolete)
        self.assertEqual(1, test_cvterm.is_relationshiptype)

    def test_get_set_cvterm_new(self):
        """Tests - get_set_cvterm - new."""
        test_dbxref = get_set_dbxref(
            db_name='test_cvterm_name_new',
            accession='test_cvterm_accession',
            description='test_cvterm_description',
            version='test_cvterm_version')

        test_cvterm = get_set_cvterm(cv_name='test_cvterm_name_new',
                                     cvterm_name='test_cvterm_name_new',
                                     dbxref=test_dbxref,
                                     definition='test_cvterm_definition',
                                     is_relationshiptype=1)

        self.assertEqual('test_cvterm_name_new', test_cvterm.name)
        self.assertEqual('test_cvterm_definition', test_cvterm.definition)
        self.assertEqual(0, test_cvterm.is_obsolete)
        self.assertEqual(1, test_cvterm.is_relationshiptype)

    def test_get_set_cvterm_existing(self):
        """Tests - get_set_cvterm - existing."""
        test_dbxref = get_set_dbxref(db_name='test_cvterm_name_existing',
                                     accession='test_cvterm_accession',
                                     description='test_cvterm_description',
                                     version='test_cvterm_version')

        test_cv = get_set_cv(cv_name='test_cvterm_name_existing',
                             definition='test_cvterm_definition')

        Cvterm.objects.create(cv=test_cv,
                              name='test_cvterm_name_existing',
                              dbxref=test_dbxref,
                              definition='test_cvterm_definition',
                              is_obsolete=1,
                              is_relationshiptype=1)

        test_cvterm = get_set_cvterm(cv_name='test_cvterm_name_existing',
                                     cvterm_name='test_cvterm_name_existing',
                                     dbxref=test_dbxref)

        self.assertEqual('test_cvterm_name_existing', test_cvterm.name)
        self.assertEqual('test_cvterm_definition', test_cvterm.definition)
        self.assertEqual(1, test_cvterm.is_obsolete)
        self.assertEqual(1, test_cvterm.is_relationshiptype)

    def test_get_set_cvterm_dbxref_new(self):
        """Tests - get_set_cvterm_dbxref - new."""
        test_dbxref = get_set_dbxref(
            db_name='test_cvterm_dbxref_name_new',
            accession='test_cvterm_dbxref_accession',
            description='test_cvterm_dbxref_description',
            version='test_cvterm_dbxref_version')

        test_cvterm = get_set_cvterm(
            cv_name='test_cvterm_dbxref_name_new',
            cvterm_name='test_cvterm_dbxref_name_new',
            dbxref=test_dbxref)

        test_cvterm_dbxref = get_set_cvterm_dbxref(cvterm=test_cvterm,
                                                   dbxref=test_dbxref,
                                                   is_for_definition=0)

        self.assertEqual(0, test_cvterm_dbxref.is_for_definition)

    def test_get_set_cvterm_dbxref_existing(self):
        """Tests - get_set_cvterm_dbxref - existing."""
        test_dbxref = get_set_dbxref(
            db_name='test_cvterm_dbxref_name_existing',
            accession='test_cvterm_dbxref_accession',
            description='test_cvterm_dbxref_description',
            version='test_cvterm_dbxref_version')

        test_cvterm = get_set_cvterm(
            cv_name='test_cvterm_dbxref_name_existing',
            cvterm_name='test_cvterm_dbxref_name_existing',
            dbxref=test_dbxref)

        CvtermDbxref.objects.create(cvterm=test_cvterm,
                                    dbxref=test_dbxref,
                                    is_for_definition=1)

        test_cvterm_dbxref = get_set_cvterm_dbxref(cvterm=test_cvterm,
                                                   dbxref=test_dbxref,
                                                   is_for_definition=1)

        self.assertEqual(1, test_cvterm_dbxref.is_for_definition)

    def test_get_set_cvtermprop_new(self):
        """Tests - get_set_cvprop - new."""
        test_dbxref = get_set_dbxref(
            db_name='test_cvtermprop_name_new',
            accession='test_cvtermprop_accession',
            description='test_cvtermprop_description',
            version='test_cvtermprop_version')

        test_cvterm = get_set_cvterm(
            cv_name='test_cvtermprop_name_new',
            cvterm_name='test_cvtermprop_name_new',
            dbxref=test_dbxref)

        test_cvterm_type = get_set_cvterm(
            cv_name='test_cvtermprop_name_type_new',
            cvterm_name='test_cvtermprop_name_type_new',
            dbxref=test_dbxref)

        test_cvtermprop = get_set_cvtermprop(
            cvterm=test_cvterm,
            type_id=test_cvterm_type.cvterm_id,
            value='test_cvterm_value_new',
            rank=1)

        self.assertEqual('test_cvterm_value_new', test_cvtermprop.value)
        self.assertEqual(1, test_cvtermprop.rank)

    def test_get_set_cvtermprop_existing(self):
        """Tests - get_set_cvprop - existing."""
        test_dbxref = get_set_dbxref(
            db_name='test_cvtermprop_name_existing',
            accession='test_cvtermprop_accession',
            description='test_cvtermprop_description',
            version='test_cvtermprop_version')

        test_cvterm = get_set_cvterm(
            cv_name='test_cvtermprop_name_existing',
            cvterm_name='test_cvtermprop_name_existing',
            dbxref=test_dbxref)

        test_cvterm_type = get_set_cvterm(
            cv_name='test_cvtermprop_name_type_existing',
            cvterm_name='test_cvtermprop_name_type_existing',
            dbxref=test_dbxref)

        Cvtermprop.objects.create(cvterm=test_cvterm,
                                  type_id=test_cvterm_type.cvterm_id,
                                  value='test_cvterm_value_existing',
                                  rank=2)

        test_cvtermprop = get_set_cvtermprop(
            cvterm=test_cvterm,
            type_id=test_cvterm_type.cvterm_id)

        self.assertEqual('test_cvterm_value_existing', test_cvtermprop.value)
        self.assertEqual(2, test_cvtermprop.rank)

    def test_get_ontology_term(self):
        """Tests - get_ontology_term."""
        test_dbxref = get_set_dbxref(
            db_name='test_ontology_term_db',
            accession='test_ontology_term_accession',
            description='test_ontology_term_description',
            version='test_ontology_term_version')

        get_set_cvterm(cv_name='test_ontology_term_cv',
                       cvterm_name='test_ontology_term_cvterm',
                       dbxref=test_dbxref)

        test_term = get_ontology_term(ontology='test_ontology_term_cv',
                                      term='test_ontology_term_cvterm')

        self.assertEqual('test_ontology_term_cvterm', test_term.name)

    def test_process_cvterm_def(self):
        """Tests - process_cvterm_def."""
        definition = '"A gene encoding ..." [SO:xp]'

        test_dbxref = get_set_dbxref(
            db_name='test_def_db',
            accession='test_def_accession')

        test_cvterm = get_set_cvterm(
            cv_name='test_def_cv',
            cvterm_name='test_def_cvterm',
            dbxref=test_dbxref)

        process_cvterm_def(test_cvterm, definition)

        test_processed_dbxref = get_dbxref(db_name='SO',
                                           accession='xp')

        test_processed_cvterm_dbxref = CvtermDbxref.objects.get(
            cvterm=test_cvterm,
            dbxref=test_processed_dbxref)

        self.assertEqual(1, test_processed_cvterm_dbxref.is_for_definition)

    def test_process_cvterm_xref(self):
        """Tests - process_cvterm_xref."""
        test_dbxref = get_set_dbxref(
            db_name='test_xref_db',
            accession='test_xref_accession')

        test_cvterm = get_set_cvterm(
            cv_name='test_xref_cv',
            cvterm_name='test_xref_cvterm',
            dbxref=test_dbxref)

        process_cvterm_xref(test_cvterm, 'SP:xq')

        test_processed_dbxref = get_dbxref(db_name='SP',
                                           accession='xq')

        test_processed_cvterm_dbxref = CvtermDbxref.objects.get(
            cvterm=test_cvterm,
            dbxref=test_processed_dbxref)

        self.assertEqual(0, test_processed_cvterm_dbxref.is_for_definition)
