# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Tests feature loader."""

from datetime import datetime, timezone

from django.test import TestCase

from machado.loaders.feature import FeatureLoader
from machado.loaders.featureattributes import FeatureAttributesLoader
from machado.models import Cv, Cvterm, Db, Dbxref, Organism
from machado.models import Feature, Featureprop, FeatureSynonym
from machado.models import FeatureCvterm, FeatureDbxref


class FeatureTest(TestCase):
    """Tests Loaders - FeatureLoader."""

    def test_get_attributes(self):
        """Tests - get attributes."""
        test_attrs_file = FeatureAttributesLoader(filecontent="genome")
        test_attrs = test_attrs_file.get_attributes("ID=1;name=feat1")
        self.assertEqual("1", test_attrs.get("id"))
        self.assertEqual("feat1", test_attrs.get("name"))

    def test_process_attributes(self):
        """Tests - get attributes."""
        test_organism = Organism.objects.create(genus="Mus", species="musculus")
        # creating test GO term
        test_db = Db.objects.create(name="GO")
        test_dbxref = Dbxref.objects.create(accession="12345", db=test_db)
        test_cv = Cv.objects.create(name="biological_process")
        Cvterm.objects.create(
            name="go test term",
            cv=test_cv,
            dbxref=test_dbxref,
            is_obsolete=0,
            is_relationshiptype=0,
        )
        # creating test SO term
        test_db = Db.objects.create(name="SO")
        test_dbxref = Dbxref.objects.create(accession="12345", db=test_db)
        test_cv = Cv.objects.create(name="sequence")
        Cvterm.objects.create(
            name="gene",
            cv=test_cv,
            dbxref=test_dbxref,
            is_obsolete=0,
            is_relationshiptype=0,
        )
        test_dbxref = Dbxref.objects.create(accession="123455", db=test_db)
        test_so_term = Cvterm.objects.create(
            name="polypeptide",
            cv=test_cv,
            dbxref=test_dbxref,
            is_obsolete=0,
            is_relationshiptype=0,
        )
        test_dbxref = Dbxref.objects.create(accession="1234555", db=test_db)
        Cvterm.objects.create(
            name="protein_match",
            cv=test_cv,
            dbxref=test_dbxref,
            is_obsolete=0,
            is_relationshiptype=0,
        )

        # creating test feature
        test_feature = Feature.objects.create(
            organism=test_organism,
            uniquename="feat1",
            is_analysis=False,
            type_id=test_so_term.cvterm_id,
            is_obsolete=False,
            timeaccessioned=datetime.now(timezone.utc),
            timelastmodified=datetime.now(timezone.utc),
        )
        # creating exact term
        test_db_global = Db.objects.create(name="_global")
        test_dbxref = Dbxref.objects.create(accession="exact", db=test_db_global)
        test_cv = Cv.objects.create(name="synonym_type")
        Cvterm.objects.create(
            name="exact",
            cv=test_cv,
            dbxref=test_dbxref,
            is_obsolete=0,
            is_relationshiptype=0,
        )
        test_db = Db.objects.create(name="RO")
        test_dbxref = Dbxref.objects.create(accession="00002", db=test_db)
        test_cv = Cv.objects.create(name="relationship")
        Cvterm.objects.create(
            name="contained in",
            cv=test_cv,
            dbxref=test_dbxref,
            is_obsolete=0,
            is_relationshiptype=0,
        )

        # new FeatureLoader
        FeatureLoader(filename="file.name", source="GFF_source")
        # running get_attributes
        test_attrs_file = FeatureAttributesLoader(filecontent="genome")
        test_attrs = test_attrs_file.get_attributes(
            "ID=1;name=feat1;note=Test feature;display=feat1;gene=gene1;"
            "orf_classification=1;ontology_term=GO:12345,GO:54321;parent=2;"
            "alias=Feature1;dbxref=GI:12345,NC:12345;noecziste=True"
        )
        # running process_attributes
        test_attrs_file.process_attributes(
            feature_id=test_feature.feature_id, attrs=test_attrs
        )
        # creating feature_property cvterm
        cv_feature_property = Cv.objects.get(name="feature_property")
        # asserting note
        test_prop_cvterm = Cvterm.objects.get(name="note", cv=cv_feature_property)
        test_prop = Featureprop.objects.get(
            feature=test_feature, type_id=test_prop_cvterm.cvterm_id, rank=0
        )
        self.assertEqual("Test feature", test_prop.value)
        # asserting ontology_term
        test_feat_cvterm = FeatureCvterm.objects.get(feature=test_feature)
        test_cvterm = Cvterm.objects.get(cvterm_id=test_feat_cvterm.cvterm_id)
        self.assertEqual("go test term", test_cvterm.name)
        # asserting dbxref
        test_dbxref_ids = FeatureDbxref.objects.filter(
            feature=test_feature
        ).values_list("dbxref_id", flat=True)
        test_db = Db.objects.get(name="GI")
        test_dbxref = Dbxref.objects.get(dbxref_id__in=test_dbxref_ids, db=test_db)
        self.assertEqual("12345", test_dbxref.accession)
        # asserting alias
        test_synonym = FeatureSynonym.objects.select_related("synonym").get(
            feature=test_feature
        )
        self.assertEqual("Feature1", test_synonym.synonym.name)
        # asserting ignored goterms
        self.assertEqual("GO:54321", test_attrs_file.ignored_goterms.pop())
