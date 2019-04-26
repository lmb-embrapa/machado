# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Tests ontology loaders."""

import os

import obonet
from django.core.management import call_command
from django.test import TestCase

from machado.loaders.ontology import OntologyLoader
from machado.models import Cv, Cvterm, Cvtermprop, Db, Dbxref
from machado.models import CvtermDbxref, Cvtermsynonym, CvtermRelationship


class OntologyTest(TestCase):
    """Tests Ontology."""

    def test_ontology(self):
        """Tests - __init__."""
        OntologyLoader("test_ontology", "test_cv_definition")
        test_ontology = Cv.objects.get(name="test_ontology")
        self.assertEqual("test_ontology", test_ontology.name)
        self.assertEqual("test_cv_definition", test_ontology.definition)

        # Testing db_internal
        test_db_internal, created = Db.objects.get_or_create(name="internal")
        self.assertEqual("internal", test_db_internal.name)
        # Testing db_OBO_REL
        test_db_obo_rel = Db.objects.get(name="OBO_REL")
        self.assertEqual("OBO_REL", test_db_obo_rel.name)
        # Testing db__global
        test_db__global = Db.objects.get(name="_global")
        self.assertEqual("_global", test_db__global.name)

        # Testing cv_synonym_type
        test_cv_synonym_type = Cv.objects.get(name="synonym_type")
        self.assertEqual("synonym_type", test_cv_synonym_type.name)
        # Testing cv_relationship
        test_cv_relationship = Cv.objects.get(name="relationship")
        self.assertEqual("relationship", test_cv_relationship.name)
        # Testing cv_cvterm_property_type
        test_cv_cvterm_property_type = Cv.objects.get(name="cvterm_property_type")
        self.assertEqual("cvterm_property_type", test_cv_cvterm_property_type.name)

        # Testing cvterm is_symmetric
        test_dbxref_is_symmetric = Dbxref.objects.get(
            accession="is_symmetric", db=test_db_internal
        )
        test_cvterm_is_symmetric = Cvterm.objects.get(
            name="is_symmetric", cv=test_cv_cvterm_property_type
        )
        self.assertEqual("is_symmetric", test_dbxref_is_symmetric.accession)
        self.assertEqual("is_symmetric", test_cvterm_is_symmetric.name)

        # Testing cvterm comment
        test_dbxref_comment = Dbxref.objects.get(
            accession="comment", db=test_db_internal
        )
        test_cvterm_comment = Cvterm.objects.get(
            name="comment", cv=test_cv_cvterm_property_type
        )
        self.assertEqual("comment", test_dbxref_comment.accession)
        self.assertEqual("comment", test_cvterm_comment.name)

        # Testing cvterm is_a
        test_dbxref_is_a = Dbxref.objects.get(accession="is_a", db=test_db_obo_rel)
        test_cvterm_is_a = Cvterm.objects.get(name="is_a", cv=test_cv_relationship)
        self.assertEqual("is_a", test_dbxref_is_a.accession)
        self.assertEqual("is_a", test_cvterm_is_a.name)

        # Testing cvterm is_transitive
        test_dbxref_is_transitive = Dbxref.objects.get(
            accession="is_transitive", db=test_db_internal
        )
        test_cvterm_is_transitive = Cvterm.objects.get(
            name="is_transitive", cv=test_cv_cvterm_property_type
        )
        self.assertEqual("is_transitive", test_dbxref_is_transitive.accession)
        self.assertEqual("is_transitive", test_cvterm_is_transitive.name)

        # Testing cvterm is_class_level
        test_dbxref_is_class_level = Dbxref.objects.get(
            accession="is_class_level", db=test_db_internal
        )
        test_cvterm_is_class_level = Cvterm.objects.get(
            name="is_class_level", cv=test_cv_cvterm_property_type
        )
        self.assertEqual("is_class_level", test_dbxref_is_class_level.accession)
        self.assertEqual("is_class_level", test_cvterm_is_class_level.name)

        # Testing cvterm is_metadata_tag
        test_dbxref_is_metadata_tag = Dbxref.objects.get(
            accession="is_metadata_tag", db=test_db_internal
        )
        test_cvterm_is_metadata_tag = Cvterm.objects.get(
            name="is_metadata_tag", cv=test_cv_cvterm_property_type
        )
        self.assertEqual("is_metadata_tag", test_dbxref_is_metadata_tag.accession)
        self.assertEqual("is_metadata_tag", test_cvterm_is_metadata_tag.name)
        # test remove_cv
        self.assertTrue(Cv.objects.filter(name="test_ontology").exists())
        call_command("remove_ontology", "--name=test_ontology", "--verbosity=0")
        self.assertFalse(Cv.objects.filter(name="test_ontology").exists())

    def test_process_cvterm_def(self):
        """Tests - process_cvterm_def."""
        definition = '"A gene encoding ..." [SO:xp]'

        ontology = OntologyLoader("test_ontology", "test_cv_definition")

        test_db, created = Db.objects.get_or_create(name="test_def_db")
        test_dbxref, created = Dbxref.objects.get_or_create(
            db=test_db, accession="test_def_accession"
        )

        test_cv, created = Cv.objects.get_or_create(name="test_def_cv")
        test_cvterm, created = Cvterm.objects.get_or_create(
            cv=test_cv,
            name="test_def_cvterm",
            dbxref=test_dbxref,
            is_relationshiptype=0,
            is_obsolete=0,
        )

        ontology.process_cvterm_def(test_cvterm, definition)

        test_processed_db = Db.objects.get(name="SO")
        test_processed_dbxref = Dbxref.objects.get(db=test_processed_db, accession="xp")

        test_processed_cvterm_dbxref = CvtermDbxref.objects.get(
            cvterm=test_cvterm, dbxref=test_processed_dbxref
        )

        self.assertEqual(1, test_processed_cvterm_dbxref.is_for_definition)

    def test_process_cvterm_xref(self):
        """Tests - process_cvterm_xref."""
        ontology = OntologyLoader("test_ontology", "test_cv_definition")

        test_db, created = Db.objects.get_or_create(name="test_xref_db")
        test_dbxref, created = Dbxref.objects.get_or_create(
            db=test_db, accession="test_xref_accession"
        )

        test_cv, created = Cv.objects.get_or_create(name="test_xref_cv")
        test_cvterm, created = Cvterm.objects.get_or_create(
            cv=test_cv,
            name="test_xref_cvterm",
            dbxref=test_dbxref,
            is_relationshiptype=0,
            is_obsolete=0,
        )

        ontology.process_cvterm_xref(test_cvterm, "SP:xq")

        test_processed_db = Db.objects.get(name="SP")
        test_processed_dbxref = Dbxref.objects.get(db=test_processed_db, accession="xq")

        test_processed_cvterm_dbxref = CvtermDbxref.objects.get(
            cvterm=test_cvterm, dbxref=test_processed_dbxref
        )

        self.assertEqual(0, test_processed_cvterm_dbxref.is_for_definition)

    def test_process_cvterm_go_synonym(self):
        """Tests - process_cvterm_go_synonym."""
        ontology = OntologyLoader("test_ontology", "test_cv_definition")

        test_db, created = Db.objects.get_or_create(name="test_go_synonym_db")
        test_dbxref, created = Dbxref.objects.get_or_create(
            db=test_db, accession="test_go_synonym_accession"
        )

        test_cv, created = Cv.objects.get_or_create(name="test_go_synonym_cv")
        test_cvterm, created = Cvterm.objects.get_or_create(
            cv=test_cv,
            name="test_go_synonym_cvterm",
            dbxref=test_dbxref,
            is_relationshiptype=0,
            is_obsolete=0,
        )

        ontology.process_cvterm_go_synonym(
            cvterm=test_cvterm,
            synonym='"30S ribosomal subunit" [GOC:mah]',
            synonym_type="related_synonym",
        )

        test_go_synonym = Cvtermsynonym.objects.get(
            cvterm=test_cvterm, synonym="30S ribosomal subunit"
        )

        self.assertEqual("30S ribosomal subunit", test_go_synonym.synonym)

    def test_process_cvterm_so_synonym(self):
        """Tests - process_cvterm_so_synonym."""
        ontology = OntologyLoader("test_ontology", "test_cv_definition")

        test_db, created = Db.objects.get_or_create(name="test_go_synonym_db")
        test_dbxref, created = Dbxref.objects.get_or_create(
            db=test_db, accession="test_so_synonym_accession"
        )

        test_cv, created = Cv.objects.get_or_create(name="test_so_synonym_cv")
        test_cvterm, created = Cvterm.objects.get_or_create(
            cv=test_cv,
            name="test_go_synonym_cvterm",
            dbxref=test_dbxref,
            is_relationshiptype=0,
            is_obsolete=0,
        )

        ontology.process_cvterm_so_synonym(
            cvterm=test_cvterm, synonym='"stop codon gained" EXACT []'
        )

        test_go_synonym = Cvtermsynonym.objects.get(cvterm=test_cvterm)
        test_go_type = Cvterm.objects.get(cvterm_id=test_go_synonym.type_id)

        self.assertEqual("stop codon gained", test_go_synonym.synonym)
        self.assertEqual("exact", test_go_type.name)

    def test_store_type_def(self):
        """Tests - store type_def."""
        directory = os.path.dirname(os.path.abspath(__file__))
        file = os.path.join(directory, "data", "so_fake.obo")

        with open(file) as obo_file:
            G = obonet.read_obo(obo_file)

        cv_name = G.graph["default-namespace"][0]
        cv_definition = G.graph["data-version"]
        # Initializing ontology
        ontology = OntologyLoader(cv_name, cv_definition)
        for typedef in G.graph["typedefs"]:
            ontology.store_type_def(typedef)

        # Testing cv
        test_cv = Cv.objects.get(name="sequence")
        self.assertEqual("sequence", test_cv.name)
        self.assertEqual("so.obo(fake)", test_cv.definition)

        # Testing store_type_def
        test_db = Db.objects.get(name="_global")
        self.assertEqual("_global", test_db.name)
        test_dbxref = Dbxref.objects.get(db=test_db, accession="derives_from")
        self.assertEqual("derives_from", test_dbxref.accession)
        test_cvterm = Cvterm.objects.get(dbxref=test_dbxref)
        self.assertEqual("derives_from", test_cvterm.name)
        self.assertEqual(
            '"testing def loading." [PMID:999090909]', test_cvterm.definition
        )
        test_type = Cvterm.objects.get(name="comment")
        test_comment = Cvtermprop.objects.get(
            cvterm_id=test_cvterm.cvterm_id, type_id=test_type.cvterm_id
        )
        self.assertEqual("Fake typedef data.", test_comment.value)
        test_type = Cvterm.objects.get(name="is_class_level")
        test_prop = Cvtermprop.objects.get(
            cvterm_id=test_cvterm.cvterm_id, type_id=test_type.cvterm_id
        )
        self.assertEqual("1", test_prop.value)
        test_type = Cvterm.objects.get(name="is_metadata_tag")
        test_prop = Cvtermprop.objects.get(
            cvterm_id=test_cvterm.cvterm_id, type_id=test_type.cvterm_id
        )
        self.assertEqual("1", test_prop.value)
        test_type = Cvterm.objects.get(name="is_symmetric")
        test_prop = Cvtermprop.objects.get(
            cvterm_id=test_cvterm.cvterm_id, type_id=test_type.cvterm_id
        )
        self.assertEqual("1", test_prop.value)
        test_type = Cvterm.objects.get(name="is_transitive")
        test_prop = Cvtermprop.objects.get(
            cvterm_id=test_cvterm.cvterm_id, type_id=test_type.cvterm_id
        )
        self.assertEqual("1", test_prop.value)
        test_dbxref = Dbxref.objects.get(accession="0123")
        test_cvterm_dbxref = CvtermDbxref.objects.get(
            cvterm=test_cvterm, dbxref=test_dbxref
        )
        self.assertEqual(0, test_cvterm_dbxref.is_for_definition)

    def test_store_term(self):
        """Tests - store term."""
        directory = os.path.dirname(os.path.abspath(__file__))
        file = os.path.join(directory, "data", "so_fake.obo")

        with open(file) as obo_file:
            G = obonet.read_obo(obo_file)

        cv_name = G.graph["default-namespace"][0]
        cv_definition = G.graph["data-version"]
        # Initializing ontology
        ontology = OntologyLoader(cv_name, cv_definition)
        for typedef in G.graph["typedefs"]:
            ontology.store_type_def(typedef)
        for n, data in G.nodes(data=True):
            ontology.store_term(n, data)

        # Testing store_term
        test_dbxref = Dbxref.objects.get(accession="0000013")
        test_cvterm = Cvterm.objects.get(dbxref=test_dbxref)
        self.assertEqual("scRNA", test_cvterm.name)
        test_def = Dbxref.objects.get(accession="ke")
        test_cvterm_dbxref = CvtermDbxref.objects.get(
            cvterm=test_cvterm, dbxref=test_def
        )
        self.assertEqual(1, test_cvterm_dbxref.is_for_definition)
        test_alt_id_dbxref = Dbxref.objects.get(accession="0000012")
        test_alt_id = CvtermDbxref.objects.get(dbxref=test_alt_id_dbxref)
        test_alt_id_cvterm = Cvterm.objects.get(cvterm_id=test_alt_id.cvterm_id)
        self.assertEqual("scRNA", test_alt_id_cvterm.name)
        test_type = Cvterm.objects.get(name="comment")
        test_comment = Cvtermprop.objects.get(
            cvterm_id=test_cvterm.cvterm_id, type_id=test_type.cvterm_id
        )
        self.assertEqual("Fake term data.", test_comment.value)
        test_dbxref = Dbxref.objects.get(accession='http://web.site/FakeData "wiki"')
        test_cvterm_dbxref = CvtermDbxref.objects.get(
            cvterm=test_cvterm, dbxref=test_dbxref
        )
        self.assertEqual(0, test_cvterm_dbxref.is_for_definition)

    def test_store_relationship(self):
        """Tests - store relationship."""
        directory = os.path.dirname(os.path.abspath(__file__))
        file = os.path.join(directory, "data", "so_fake.obo")

        with open(file) as obo_file:
            G = obonet.read_obo(obo_file)

        cv_name = G.graph["default-namespace"][0]
        cv_definition = G.graph["data-version"]
        # Initializing ontology
        ontology = OntologyLoader(cv_name, cv_definition)
        for typedef in G.graph["typedefs"]:
            ontology.store_type_def(typedef)
        for n, data in G.nodes(data=True):
            ontology.store_term(n, data)
        for u, v, type in G.edges(keys=True):
            ontology.store_relationship(u, v, type)

        # Testing store_term
        test_subject_dbxref = Dbxref.objects.get(accession="0000013")
        test_subject_cvterm = Cvterm.objects.get(dbxref=test_subject_dbxref)
        self.assertEqual("scRNA", test_subject_cvterm.name)
        test_object_dbxref = Dbxref.objects.get(accession="0000012")
        test_object_cvterm = Cvterm.objects.get(dbxref=test_object_dbxref)
        self.assertEqual("scRNA_primary_transcript", test_object_cvterm.name)

        test_type = CvtermRelationship.objects.get(
            subject=test_subject_cvterm, object=test_object_cvterm
        )
        test_type_cvterm = Cvterm.objects.get(cvterm_id=test_type.type_id)
        self.assertEqual("derives_from", test_type_cvterm.name)
