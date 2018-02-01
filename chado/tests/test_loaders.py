"""Tests loaders functions."""

from chado.loaders.common import process_cvterm_def, process_cvterm_xref
from chado.loaders.common import process_cvterm_go_synonym
from chado.models import CvtermDbxref, Cvtermsynonym
from chado.models import Cv, Cvterm, Db, Dbxref
from django.test import TestCase


class CommonTest(TestCase):
    """Tests Loaders - Common."""

    def test_process_cvterm_def(self):
        """Tests - process_cvterm_def."""
        definition = '"A gene encoding ..." [SO:xp]'

        test_db, created = Db.objects.get_or_create(name='test_def_db')
        test_dbxref, created = Dbxref.objects.get_or_create(
            db=test_db, accession='test_def_accession')

        test_cv, created = Cv.objects.get_or_create(
            name='test_def_cv')
        test_cvterm, created = Cvterm.objects.get_or_create(
            cv=test_cv,
            name='test_def_cvterm',
            dbxref=test_dbxref,
            is_relationshiptype=0,
            is_obsolete=0)

        process_cvterm_def(test_cvterm, definition)

        test_processed_db = Db.objects.get(name='SO')
        test_processed_dbxref = Dbxref.objects.get(db=test_processed_db,
                                                   accession='xp')

        test_processed_cvterm_dbxref = CvtermDbxref.objects.get(
            cvterm=test_cvterm,
            dbxref=test_processed_dbxref)

        self.assertEqual(1, test_processed_cvterm_dbxref.is_for_definition)

    def test_process_cvterm_xref(self):
        """Tests - process_cvterm_xref."""
        test_db, created = Db.objects.get_or_create(name='test_xref_db')
        test_dbxref, created = Dbxref.objects.get_or_create(
            db=test_db,
            accession='test_xref_accession')

        test_cv, created = Cv.objects.get_or_create(name='test_xref_cv')
        test_cvterm, created = Cvterm.objects.get_or_create(
            cv=test_cv,
            name='test_xref_cvterm',
            dbxref=test_dbxref,
            is_relationshiptype=0,
            is_obsolete=0)

        process_cvterm_xref(test_cvterm, 'SP:xq')

        test_processed_db = Db.objects.get(name='SP')
        test_processed_dbxref = Dbxref.objects.get(
            db=test_processed_db,
            accession='xq')

        test_processed_cvterm_dbxref = CvtermDbxref.objects.get(
            cvterm=test_cvterm,
            dbxref=test_processed_dbxref)

        self.assertEqual(0, test_processed_cvterm_dbxref.is_for_definition)

    def test_process_cvterm_go_synonym(self):
        """Tests - process_cvterm_go_synonym."""
        test_db, created = Db.objects.get_or_create(name='test_go_synonym_db')
        test_dbxref, created = Dbxref.objects.get_or_create(
            db=test_db,
            accession='test_go_synonym_accession')

        test_cv, created = Cv.objects.get_or_create(
            name='test_go_synonym_cv')
        test_cvterm, created = Cvterm.objects.get_or_create(
            cv=test_cv,
            name='test_go_synonym_cvterm',
            dbxref=test_dbxref,
            is_relationshiptype=0,
            is_obsolete=0)

        process_cvterm_go_synonym(cvterm=test_cvterm,
                                  synonym='"30S ribosomal subunit" [GOC:mah]',
                                  synonym_type='related_synonym')

        test_go_synonym = Cvtermsynonym.objects.get(
            cvterm=test_cvterm,
            synonym='30S ribosomal subunit')

        self.assertEqual('30S ribosomal subunit', test_go_synonym.synonym)
