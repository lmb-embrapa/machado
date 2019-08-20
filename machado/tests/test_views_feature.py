# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Tests feature view."""

from datetime import datetime, timezone

from django.test import TestCase, RequestFactory
from django.urls.exceptions import NoReverseMatch

from machado.models import Analysis, Analysisfeature
from machado.models import Db, Dbxref, Cv, Cvterm, Organism, Pub
from machado.models import Feature, Featureloc, FeatureDbxref, FeatureCvterm
from machado.models import Featureprop, FeatureRelationship
from machado.views import feature


class FeatureTest(TestCase):
    """Tests Feature View."""

    def setUp(self):
        """Setup."""
        self.factory = RequestFactory()

        null_db, created = Db.objects.get_or_create(name="null")
        null_cv, created = Cv.objects.get_or_create(name="null")
        null_dbxref, created = Dbxref.objects.get_or_create(
            accession="null", db=null_db
        )

        null_cvterm, created = Cvterm.objects.get_or_create(
            name="null",
            cv=null_cv,
            dbxref=null_dbxref,
            is_obsolete=0,
            is_relationshiptype=0,
        )
        null_pub, created = Pub.objects.get_or_create(
            uniquename="null", type=null_cvterm, is_obsolete=False
        )

        ro_db = Db.objects.create(name="RO")
        ro_cv = Cv.objects.create(name="relationship")
        similarity_dbxref = Dbxref.objects.create(
            accession="in similarity relationship with", db=ro_db
        )
        similarity_cvterm = Cvterm.objects.create(
            name="in similarity relationship with",
            cv=ro_cv,
            dbxref=similarity_dbxref,
            is_obsolete=0,
            is_relationshiptype=0,
        )
        fp_db = Db.objects.create(name="feature_property")
        fp_cv = Cv.objects.create(name="feature_property")
        orthology_dbxref = Dbxref.objects.create(
            accession="orthologous group", db=fp_db
        )
        orthology_cvterm = Cvterm.objects.create(
            name="orthologous group",
            cv=fp_cv,
            dbxref=orthology_dbxref,
            is_obsolete=0,
            is_relationshiptype=0,
        )
        coexpgroup_dbxref = Dbxref.objects.create(
            accession="coexpression group", db=fp_db
        )
        coexpgroup_cvterm = Cvterm.objects.create(
            name="coexpression group",
            cv=fp_cv,
            dbxref=coexpgroup_dbxref,
            is_obsolete=0,
            is_relationshiptype=0,
        )

        so_db = Db.objects.create(name="SO")
        so_cv = Cv.objects.create(name="sequence")
        chromosome_dbxref = Dbxref.objects.create(accession="chromosome", db=so_db)
        chromosome_cvterm = Cvterm.objects.create(
            name="chromosome",
            cv=so_cv,
            dbxref=chromosome_dbxref,
            is_obsolete=0,
            is_relationshiptype=0,
        )
        gene_dbxref = Dbxref.objects.create(accession="gene", db=so_db)
        gene_cvterm = Cvterm.objects.create(
            name="gene",
            cv=so_cv,
            dbxref=gene_dbxref,
            is_obsolete=0,
            is_relationshiptype=0,
        )
        mRNA_dbxref = Dbxref.objects.create(accession="mRNA", db=so_db)
        mRNA_cvterm = Cvterm.objects.create(
            name="mRNA",
            cv=so_cv,
            dbxref=mRNA_dbxref,
            is_obsolete=0,
            is_relationshiptype=0,
        )
        tRNA_dbxref = Dbxref.objects.create(accession="tRNA", db=so_db)
        tRNA_cvterm = Cvterm.objects.create(
            name="tRNA",
            cv=so_cv,
            dbxref=tRNA_dbxref,
            is_obsolete=0,
            is_relationshiptype=0,
        )
        polypeptide_dbxref = Dbxref.objects.create(accession="polypeptide", db=so_db)
        polypeptide_cvterm = Cvterm.objects.create(
            name="polypeptide",
            cv=so_cv,
            dbxref=polypeptide_dbxref,
            is_obsolete=0,
            is_relationshiptype=0,
        )
        protein_match_dbxref = Dbxref.objects.create(
            accession="protein_match", db=so_db
        )
        protein_match_cvterm = Cvterm.objects.create(
            name="protein_match",
            cv=so_cv,
            dbxref=protein_match_dbxref,
            is_obsolete=0,
            is_relationshiptype=0,
        )
        match_part_dbxref = Dbxref.objects.create(accession="match_part", db=so_db)
        match_part_cvterm = Cvterm.objects.create(
            name="match_part",
            cv=so_cv,
            dbxref=match_part_dbxref,
            is_obsolete=0,
            is_relationshiptype=0,
        )

        part_of_dbxref = Dbxref.objects.create(accession="part_of", db=so_db)
        part_of_cvterm = Cvterm.objects.create(
            name="part_of",
            cv=so_cv,
            dbxref=part_of_dbxref,
            is_obsolete=0,
            is_relationshiptype=0,
        )
        translation_of_dbxref = Dbxref.objects.create(
            accession="translation_of", db=so_db
        )
        translation_of_cvterm = Cvterm.objects.create(
            name="translation_of",
            cv=so_cv,
            dbxref=translation_of_dbxref,
            is_obsolete=0,
            is_relationshiptype=0,
        )

        self.organism1 = Organism.objects.create(genus="Mus", species="musculus")
        multispecies_organism = Organism.objects.create(
            genus="multispecies", species="multispecies"
        )

        chromosome_chr1 = Feature.objects.create(
            organism=self.organism1,
            uniquename="chr1",
            is_analysis=False,
            type=chromosome_cvterm,
            is_obsolete=False,
            timeaccessioned=datetime.now(timezone.utc),
            timelastmodified=datetime.now(timezone.utc),
        )
        gene_feat1 = Feature.objects.create(
            organism=self.organism1,
            uniquename="feat1",
            is_analysis=False,
            type=gene_cvterm,
            is_obsolete=False,
            timeaccessioned=datetime.now(timezone.utc),
            timelastmodified=datetime.now(timezone.utc),
        )
        mRNA_feat1 = Feature.objects.create(
            organism=self.organism1,
            uniquename="feat1",
            is_analysis=False,
            type=mRNA_cvterm,
            is_obsolete=False,
            timeaccessioned=datetime.now(timezone.utc),
            timelastmodified=datetime.now(timezone.utc),
        )
        Feature.objects.create(
            organism=self.organism1,
            uniquename="tfeat1",
            is_analysis=False,
            type=tRNA_cvterm,
            is_obsolete=False,
            timeaccessioned=datetime.now(timezone.utc),
            timelastmodified=datetime.now(timezone.utc),
        )

        polypeptide_db = Db.objects.create(name="GFF_SOURCE")

        polypeptide_feat1_dbxref = Dbxref.objects.create(
            accession="feat1", db=polypeptide_db
        )
        polypeptide_feat1 = Feature.objects.create(
            organism=self.organism1,
            uniquename="feat1",
            dbxref=polypeptide_feat1_dbxref,
            is_analysis=False,
            type=polypeptide_cvterm,
            is_obsolete=False,
            timeaccessioned=datetime.now(timezone.utc),
            timelastmodified=datetime.now(timezone.utc),
        )

        polypeptide_feat2_dbxref = Dbxref.objects.create(
            accession="feat2", db=polypeptide_db
        )
        polypeptide_feat2 = Feature.objects.create(
            organism=self.organism1,
            uniquename="feat2",
            dbxref=polypeptide_feat2_dbxref,
            is_analysis=False,
            type=polypeptide_cvterm,
            is_obsolete=False,
            timeaccessioned=datetime.now(timezone.utc),
            timelastmodified=datetime.now(timezone.utc),
        )

        FeatureRelationship.objects.create(
            object=mRNA_feat1, subject=gene_feat1, type=part_of_cvterm, rank=0
        )
        FeatureRelationship.objects.create(
            object=polypeptide_feat1,
            subject=mRNA_feat1,
            type=translation_of_cvterm,
            rank=0,
        )

        protein_match_PF1_db = Db.objects.create(name="PFAM")
        protein_match_PF1_dbxref = Dbxref.objects.create(
            accession="0001", db=protein_match_PF1_db
        )

        protein_match_PF1 = Feature.objects.create(
            organism=multispecies_organism,
            uniquename="PF0001",
            name="PF0001 PF0001",
            dbxref=protein_match_PF1_dbxref,
            type=protein_match_cvterm,
            is_analysis=False,
            is_obsolete=False,
            timeaccessioned=datetime.now(timezone.utc),
            timelastmodified=datetime.now(timezone.utc),
        )

        Featureloc.objects.create(
            feature=mRNA_feat1,
            srcfeature=chromosome_chr1,
            strand=1,
            fmin=1,
            is_fmin_partial=False,
            fmax=1000,
            is_fmax_partial=False,
            locgroup=0,
            rank=0,
        )

        mRNA_feat1_db = Db.objects.create(name="GI")
        mRNA_feat1_dbxref = Dbxref.objects.create(accession="12345", db=mRNA_feat1_db)
        FeatureDbxref.objects.create(
            feature=mRNA_feat1, dbxref=mRNA_feat1_dbxref, is_current=True
        )

        molfun_db = Db.objects.create(name="GO")
        molfun_dbxref = Dbxref.objects.create(accession="00001", db=molfun_db)
        go_cv = Cv.objects.create(name="molecular function")
        go_cvterm = Cvterm.objects.create(
            name="teste",
            definition="teste teste",
            dbxref=molfun_dbxref,
            cv=go_cv,
            is_obsolete=0,
            is_relationshiptype=0,
        )
        FeatureCvterm.objects.create(
            feature=mRNA_feat1, cvterm=go_cvterm, pub=null_pub, is_not=False, rank=0
        )

        FeatureRelationship.objects.create(
            object=polypeptide_feat1,
            subject=protein_match_PF1,
            type=similarity_cvterm,
            rank=0,
        )

        match_part_feat = Feature.objects.create(
            organism=self.organism1,
            uniquename="match_part1",
            is_analysis=False,
            type=match_part_cvterm,
            is_obsolete=False,
            timeaccessioned=datetime.now(timezone.utc),
            timelastmodified=datetime.now(timezone.utc),
        )

        analysis = Analysis.objects.create(
            program="blast",
            programversion="2.2.31+",
            timeexecuted=datetime.now(timezone.utc),
        )
        Analysisfeature.objects.create(
            analysis=analysis,
            feature=match_part_feat,
            normscore=1000,
            significance=0.0001,
        )
        Featureloc.objects.create(
            feature=match_part_feat,
            srcfeature=polypeptide_feat1,
            strand=1,
            fmin=20,
            is_fmin_partial=False,
            fmax=2000,
            is_fmax_partial=False,
            locgroup=0,
            rank=0,
        )
        Featureloc.objects.create(
            feature=match_part_feat,
            srcfeature=polypeptide_feat2,
            strand=1,
            fmin=30,
            is_fmin_partial=False,
            fmax=3000,
            is_fmax_partial=False,
            locgroup=1,
            rank=0,
        )

        Featureprop.objects.create(
            feature=polypeptide_feat1, type=orthology_cvterm, rank=0, value="orthomcl1"
        )
        Featureprop.objects.create(
            feature=polypeptide_feat2, type=orthology_cvterm, rank=0, value="orthomcl1"
        )
        Featureprop.objects.create(
            feature=polypeptide_feat1,
            type=coexpgroup_cvterm,
            rank=0,
            value="coexpgroup1",
        )
        Featureprop.objects.create(
            feature=polypeptide_feat2,
            type=coexpgroup_cvterm,
            rank=0,
            value="coexpgroup1",
        )

    def test_retrieve_feature_location(self):
        """Tests - retrieve_feature_location."""
        fv = feature.FeatureView()
        f = Feature.objects.get(uniquename="feat1", type__name="mRNA")
        result = fv.retrieve_feature_location(
            feature_id=f.feature_id, organism="Mus musculus"
        )
        self.assertEqual(1, result[0]["start"])
        self.assertEqual(1000, result[0]["end"])
        self.assertEqual(1, result[0]["strand"])
        self.assertEqual("chr1", result[0]["ref"])

    def test_retrieve_feature_dbxref(self):
        """Tests - retrieve_feature_dbxref."""
        fv = feature.FeatureView()
        f = Feature.objects.get(uniquename="feat1", type__name="mRNA")
        result = fv.retrieve_feature_dbxref(feature_id=f.feature_id)
        self.assertEqual("GI", result[0]["db"])
        self.assertEqual("12345", result[0]["dbxref"])

    def test_retrieve_feature_cvterm(self):
        """Tests - retrieve_feature_cvterm."""
        fv = feature.FeatureView()
        f = Feature.objects.get(uniquename="feat1", type__name="mRNA")
        result = fv.retrieve_feature_cvterm(feature_id=f.feature_id)
        self.assertEqual("teste", result[0]["cvterm"])
        self.assertEqual("teste teste", result[0]["cvterm_definition"])
        self.assertEqual("molecular function", result[0]["cv"])
        self.assertEqual("GO", result[0]["db"])
        self.assertEqual("00001", result[0]["dbxref"])

    def test_retrieve_feature_protein_matches(self):
        """Tests - retrieve_feature_protein_matches."""
        fv = feature.FeatureView()
        f = Feature.objects.get(uniquename="feat1", type__name="polypeptide")
        result = fv.retrieve_feature_protein_matches(feature_id=f.feature_id)
        self.assertEqual("PF0001", result[0]["subject_id"])
        self.assertEqual("PF0001 PF0001", result[0]["subject_desc"])
        self.assertEqual("PFAM", result[0]["db"])
        self.assertEqual("0001", result[0]["dbxref"])

    def test_retrieve_feature_similarity(self):
        """Tests - retrieve_feature_similarity."""
        fv = feature.FeatureView()
        f = Feature.objects.get(uniquename="feat1", type__name="polypeptide")
        result = fv.retrieve_feature_similarity(
            feature_id=f.feature_id, organism_id=self.organism1.organism_id
        )
        self.assertEqual("blast", result[0]["program"])
        self.assertEqual("2.2.31+", result[0]["programversion"])
        self.assertEqual("feat2", result[0]["unique"])
        self.assertEqual(20, result[0]["query_start"])
        self.assertEqual(2000, result[0]["query_end"])
        self.assertEqual(0.0001, result[0]["evalue"])
        self.assertEqual(1000, result[0]["score"])

    def test_retrieve_feature_orthologs(self):
        """Tests - retrieve_feature_orthologs."""
        fv = feature.FeatureView()
        f = Feature.objects.get(uniquename="feat1", type__name="polypeptide")
        result = fv.retrieve_feature_orthologs(feature_id=f.feature_id)
        self.assertTrue("orthomcl1" in result)
        self.assertEquals("feat2", result["orthomcl1"][1].uniquename)

    def test_retrieve_feature_data(self):
        """Tests - retrieve_feature_data."""
        fv = feature.FeatureView()
        f = Feature.objects.get(uniquename="feat1", type__name="mRNA")
        result = fv.retrieve_feature_data(feature_obj=f)
        self.assertEquals(1, result["location"][0]["start"])
        self.assertEquals("GI", result["dbxref"][0]["db"])
        self.assertEquals("GO", result["cvterm"][0]["db"])

        f = Feature.objects.get(uniquename="feat1", type__name="polypeptide")
        result = fv.retrieve_feature_data(feature_obj=f)
        self.assertEquals("PFAM", result["protein_matches"][0]["db"])
        self.assertEqual("blast", result["similarity"][0]["program"])
        self.assertTrue("orthomcl1" in result["orthologs"])

    def test_get(self):
        """Tests - get."""
        f = Feature.objects.get(uniquename="feat1", type__name="mRNA")
        request = self.factory.get("/feature/?feature_id={}".format(f.feature_id))
        fv = feature.FeatureView()

        try:
            response = fv.get(request)
        except NoReverseMatch:
            return

        self.assertEqual(response.status_code, 200)

        f = Feature.objects.get(uniquename="tfeat1", type__name="tRNA")
        request = self.factory.get("/feature/?feature_id={}".format(f.feature_id))
        fv = feature.FeatureView()

        try:
            response = fv.get(request)
        except NoReverseMatch:
            return

        self.assertContains(response, "Invalid feature type.")

        request = self.factory.get("/feature/?feature_id=123456789")
        fv = feature.FeatureView()
        response = fv.get(request)
        self.assertContains(response, "Feature not found.")
