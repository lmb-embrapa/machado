# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Tests for the rebuild_search_index management command helpers."""

from django.test import TestCase

from machado.models import (
    Organism,
    Feature,
    FeatureSearchIndex,
    Cvterm,
    Cv,
    Dbxref,
    Db,
)


class SearchVectorGeneratedColumnTest(TestCase):
    """The search_vector column is maintained by PostgreSQL, not by Python."""

    def test_search_vector_populates_on_insert(self):
        """Inserting a row computes search_vector without an explicit update."""
        db = Db.objects.create(name="gc_db")
        dbxref = Dbxref.objects.create(db=db, accession="gc_acc", version="1")
        cv = Cv.objects.create(name="sequence")
        cvterm = Cvterm.objects.create(
            name="gene", cv=cv, dbxref=dbxref, is_obsolete=0, is_relationshiptype=0
        )
        org = Organism.objects.create(genus="Gen", species="spec")
        feature = Feature.objects.create(
            organism=org,
            uniquename="gc_feature",
            name="GC Feature",
            type=cvterm,
            is_analysis=False,
            is_obsolete=False,
            timeaccessioned="2023-01-01T00:00:00Z",
            timelastmodified="2023-01-01T00:00:00Z",
        )
        FeatureSearchIndex.objects.create(
            feature=feature, autocomplete_text="kinase transporter"
        )
        row = FeatureSearchIndex.objects.get(feature=feature)
        self.assertIsNotNone(row.search_vector)
        self.assertIn(
            "kinas",
            str(row.search_vector),
            "generated tsvector should contain the indexed lexeme",
        )

    def test_search_vector_tracks_autocomplete_text_updates(self):
        """Changing autocomplete_text re-computes search_vector automatically."""
        db = Db.objects.create(name="gc_db2")
        dbxref = Dbxref.objects.create(db=db, accession="gc_acc2", version="1")
        cv = Cv.objects.create(name="sequence")
        cvterm = Cvterm.objects.create(
            name="gene", cv=cv, dbxref=dbxref, is_obsolete=0, is_relationshiptype=0
        )
        org = Organism.objects.create(genus="Gen", species="spec2")
        feature = Feature.objects.create(
            organism=org,
            uniquename="gc_feature2",
            type=cvterm,
            is_analysis=False,
            is_obsolete=False,
            timeaccessioned="2023-01-01T00:00:00Z",
            timelastmodified="2023-01-01T00:00:00Z",
        )
        row = FeatureSearchIndex.objects.create(
            feature=feature, autocomplete_text="original"
        )
        row.autocomplete_text = "replaced"
        row.save(update_fields=["autocomplete_text"])
        row.refresh_from_db()
        self.assertIn("replac", str(row.search_vector))
