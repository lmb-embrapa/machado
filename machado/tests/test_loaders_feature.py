# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Tests feature loader."""

from datetime import datetime, timezone

from Bio.SearchIO._model import Hit
from bibtexparser.bibdatabase import BibDatabase
from django.test import TestCase

from machado.loaders.feature import FeatureLoader
from machado.loaders.publication import PublicationLoader
from machado.models import Cv, Cvterm, Db, Dbxref, Organism
from machado.models import Feature, Featureprop, FeatureSynonym
from machado.models import FeatureCvterm, FeatureDbxref
from machado.models import Featureloc, FeatureRelationship
from machado.models import Pub, PubDbxref, FeaturePub


class FeatureTest(TestCase):
    """Tests Loaders - FeatureLoader."""

    def test_get_attributes(self):
        """Tests - get attributes."""
        test_db = Db.objects.create(name="SO")
        test_dbxref = Dbxref.objects.create(accession="12345", db=test_db)
        test_cv = Cv.objects.create(name="sequence")
        Cvterm.objects.create(
            name="polypeptide",
            cv=test_cv,
            dbxref=test_dbxref,
            is_obsolete=0,
            is_relationshiptype=0,
        )
        test_dbxref = Dbxref.objects.create(accession="123455", db=test_db)
        Cvterm.objects.create(
            name="protein_match",
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

        Organism.objects.create(genus="Mus", species="musculus")
        test_feature_file = FeatureLoader(filename="file.name", source="GFF_loader")
        test_attrs = test_feature_file.get_attributes("ID=1;name=feat1")
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
        test_so_term = Cvterm.objects.create(
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
        test_so_term = Cvterm.objects.create(
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
        test_feature_file = FeatureLoader(filename="file.name", source="GFF_source")
        # running get_attributes
        test_attrs = test_feature_file.get_attributes(
            "ID=1;name=feat1;note=Test feature;display=feat1;gene=gene1;"
            "orf_classification=1;ontology_term=GO:12345,GO:54321;parent=2;"
            "alias=Feature1;dbxref=GI:12345,NC:12345;noecziste=True"
        )
        # running process_attributes
        test_feature_file.process_attributes(
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
        self.assertEqual("GO:54321", test_feature_file.ignored_goterms.pop())

    def test_store_tabix_feature(self):
        """Tests - store tabix feature / store relationships."""
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
        # creating part_of term
        test_dbxref = Dbxref.objects.create(accession="part_of", db=test_db_global)
        test_cv = Cv.objects.create(name="sequence")
        Cvterm.objects.create(
            name="part_of",
            cv=test_cv,
            dbxref=test_dbxref,
            is_obsolete=0,
            is_relationshiptype=0,
        )
        # create SO terms: assembly, gene, and exon
        test_db = Db.objects.create(name="SO")
        test_dbxref = Dbxref.objects.create(accession="00001", db=test_db)
        test_cvterm_assembly = Cvterm.objects.create(
            name="assembly",
            cv=test_cv,
            dbxref=test_dbxref,
            is_obsolete=0,
            is_relationshiptype=0,
        )
        test_dbxref = Dbxref.objects.create(accession="00002", db=test_db)
        Cvterm.objects.create(
            name="gene",
            cv=test_cv,
            dbxref=test_dbxref,
            is_obsolete=0,
            is_relationshiptype=0,
        )
        test_dbxref = Dbxref.objects.create(accession="00003", db=test_db)
        Cvterm.objects.create(
            name="exon",
            cv=test_cv,
            dbxref=test_dbxref,
            is_obsolete=0,
            is_relationshiptype=0,
        )
        test_dbxref = Dbxref.objects.create(accession="00004", db=test_db)
        Cvterm.objects.create(
            name="polypeptide",
            cv=test_cv,
            dbxref=test_dbxref,
            is_obsolete=0,
            is_relationshiptype=0,
        )
        test_dbxref = Dbxref.objects.create(accession="00005", db=test_db)
        Cvterm.objects.create(
            name="protein_match",
            cv=test_cv,
            dbxref=test_dbxref,
            is_obsolete=0,
            is_relationshiptype=0,
        )
        # create RO term: contained in
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

        # create an organism
        test_organism = Organism.objects.create(genus="Mus", species="musculus")
        # create a srcfeature
        test_db = Db.objects.create(name="FASTA_SOURCE")
        test_dbxref = Dbxref.objects.create(accession="contig1", db=test_db)
        feature = Feature.objects.create(
            dbxref=test_dbxref,
            organism=test_organism,
            name="contig1",
            type=test_cvterm_assembly,
            uniquename="contig1",
            is_analysis=False,
            is_obsolete=False,
            timeaccessioned=datetime.now(timezone.utc),
            timelastmodified=datetime.now(timezone.utc),
        )

        # DOI TESTING
        db2 = BibDatabase()
        db2.entries = [
            {
                "journal": "Nice Journal",
                "comments": "A comment",
                "pages": "12--23",
                "month": "jan",
                "abstract": "This is an abstract. This line should be "
                "long enough to test multilines...",
                "title": "An amazing title",
                "year": "2013",
                "doi": "10.1186/s12864-016-2535-300002",
                "volume": "12",
                "ID": "Teste2018",
                "author": "Foo, b. and Foo1, b. and Foo b.",
                "keyword": "keyword1, keyword2",
                "ENTRYTYPE": "article",
            }
        ]
        for entry in db2.entries:
            bibtest3 = PublicationLoader()
            bibtest3.store_bibtex_entry(entry)
        test_bibtex3 = Pub.objects.get(uniquename="Teste2018")
        test_bibtex3_pubdbxref = PubDbxref.objects.get(pub=test_bibtex3)
        test_bibtex3_dbxref = Dbxref.objects.get(
            dbxref_id=test_bibtex3_pubdbxref.dbxref_id
        )
        self.assertEqual(
            "10.1186/s12864-016-2535-300002", test_bibtex3_dbxref.accession
        )
        # DOI: try to link feature to publication's DOI
        featurepub_test = None
        if feature and test_bibtex3_pubdbxref:
            featurepub_test = FeaturePub.objects.create(
                feature_id=feature.feature_id, pub_id=test_bibtex3_pubdbxref.pub_id
            )
        test_pub = Pub.objects.get(pub_id=featurepub_test.pub_id)
        self.assertEqual("An amazing title", test_pub.title)
        test_pubdbxref = PubDbxref.objects.get(pub=test_pub)
        test_dbxref = Dbxref.objects.get(dbxref_id=test_pubdbxref.dbxref_id)
        self.assertEqual("10.1186/s12864-016-2535-300002", test_dbxref.accession)

        # create a tabix feature
        class TabixFeature(object):
            """mock tabix feature."""

        test_tabix_feature1 = TabixFeature()
        test_tabix_feature1.contig = "contig1"
        test_tabix_feature1.feature = "gene"
        test_tabix_feature1.start = "10"
        test_tabix_feature1.end = "100"
        test_tabix_feature1.strand = "+"
        test_tabix_feature1.frame = "1"
        test_tabix_feature1.attributes = "id=id1;name=name1"

        test_tabix_feature2 = TabixFeature()
        test_tabix_feature2.contig = "contig1"
        test_tabix_feature2.feature = "exon"
        test_tabix_feature2.start = "10"
        test_tabix_feature2.end = "100"
        test_tabix_feature2.strand = "-"
        test_tabix_feature2.frame = "2"
        test_tabix_feature2.attributes = "id=id2;name=name2;parent=id1"

        # instantiate the loader
        test_feature_file = FeatureLoader(filename="file.name", source="GFF_source")

        organism = "Mus musculus"
        # store the tabix feature
        test_feature_file.store_tabix_feature(test_tabix_feature1, organism)
        test_feature_file.store_tabix_feature(test_tabix_feature2, organism)

        # store the relationships
        test_feature_file.store_relationships(organism)

        test_feature = Feature.objects.get(uniquename="id2")
        test_featureloc = Featureloc.objects.get(feature=test_feature)
        test_feature_relationship = FeatureRelationship.objects.get(
            object=test_feature.feature_id
        )
        test_src_feature = Feature.objects.get(
            feature_id=test_feature_relationship.subject.feature_id
        )
        self.assertEqual("name2", test_feature.name)
        self.assertEqual(10, test_featureloc.fmin)
        self.assertEqual("id1", test_src_feature.uniquename)

    def test_store_bio_searchio_hit(self):
        """Tests - store bio searchio hit."""
        # create RO term: contained in
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

        # create SO terms: protein_match
        test_cv = Cv.objects.create(name="sequence")
        test_db = Db.objects.create(name="SO")
        test_dbxref = Dbxref.objects.create(accession="00001", db=test_db)
        Cvterm.objects.create(
            name="protein_match",
            cv=test_cv,
            dbxref=test_dbxref,
            is_obsolete=0,
            is_relationshiptype=0,
        )
        test_dbxref = Dbxref.objects.create(accession="00002", db=test_db)
        Cvterm.objects.create(
            name="polypeptide",
            cv=test_cv,
            dbxref=test_dbxref,
            is_obsolete=0,
            is_relationshiptype=0,
        )
        # create GO term
        test_db = Db.objects.create(name="GO")
        test_dbxref = Dbxref.objects.create(accession="1234", db=test_db)
        test_cv = Cv.objects.create(name="biological_process")
        Cvterm.objects.create(
            name="GO:1234",
            cv=test_cv,
            dbxref=test_dbxref,
            is_obsolete=0,
            is_relationshiptype=0,
        )

        # create a bio searchio hit
        test_searchio_hit = Hit()
        test_searchio_hit.id = "PF1234"
        test_searchio_hit.accession = "PFAM mock domain"
        test_searchio_hit.attributes["Target"] = "PFAM"
        test_searchio_hit.dbxrefs = ["GO:1234", "IPR:IPR012345", "Reactome:R-HSA-12345"]

        Organism.objects.create(genus="test", species="organism")

        # instantiate the loader
        test_feature_file = FeatureLoader(
            filename="file.name", source="InterproScan_source"
        )
        # store the bio searchio hit
        # From interproscan
        target = "InterPro"
        test_feature_file.store_bio_searchio_hit(test_searchio_hit, target)

        test_feature = Feature.objects.get(uniquename="PF1234")
        self.assertEqual("PFAM mock domain", test_feature.name)

        test_dbxref = Dbxref.objects.get(accession="IPR012345")
        test_feature_dbxref = FeatureDbxref.objects.get(
            feature=test_feature, dbxref=test_dbxref
        )
        self.assertEqual(True, test_feature_dbxref.is_current)

        test_cvterm = Cvterm.objects.get(name="GO:1234")
        test_feature_cvterm = FeatureCvterm.objects.get(
            feature=test_feature, cvterm=test_cvterm
        )
        self.assertEqual(0, test_feature_cvterm.rank)

    def test_store_feature_annotation(self):
        """Tests - store feature annotation."""
        # creating exact term
        test_db_global = Db.objects.create(name="_global")
        test_dbxref = Dbxref.objects.create(accession="exact", db=test_db_global)
        test_cv = Cv.objects.create(name="synonym_type")
        test_so_term = Cvterm.objects.create(
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

        test_db = Db.objects.create(name="SO")
        test_dbxref = Dbxref.objects.create(accession="12345", db=test_db)
        test_cv = Cv.objects.create(name="sequence")
        test_so_term = Cvterm.objects.create(
            name="polypeptide",
            cv=test_cv,
            dbxref=test_dbxref,
            is_obsolete=0,
            is_relationshiptype=0,
        )
        test_dbxref = Dbxref.objects.create(accession="123455", db=test_db)
        Cvterm.objects.create(
            name="protein_match",
            cv=test_cv,
            dbxref=test_dbxref,
            is_obsolete=0,
            is_relationshiptype=0,
        )

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

        test_organism = Organism.objects.create(genus="Mus", species="musculus")

        test_db = Db.objects.create(name="GFF_SOURCE")
        test_dbxref = Dbxref.objects.create(accession="feat2", db=test_db)
        test_feature = Feature.objects.create(
            organism=test_organism,
            uniquename="feat2",
            dbxref=test_dbxref,
            is_analysis=False,
            type_id=test_so_term.cvterm_id,
            is_obsolete=False,
            timeaccessioned=datetime.now(timezone.utc),
            timelastmodified=datetime.now(timezone.utc),
        )

        test_feature_file = FeatureLoader(filename="file.name", source="GFF_loader")

        # store the feature annotation
        test_feature_file.store_feature_annotation(
            feature="feat2",
            soterm="polypeptide",
            cvterm="display",
            annotation="feature one",
        )
        test_featureprop = Featureprop.objects.get(feature=test_feature)
        self.assertEqual("feature one", test_featureprop.value)

        # replace the feature annotation
        test_feature_file.store_feature_annotation(
            feature="feat2",
            soterm="polypeptide",
            cvterm="display",
            annotation="feature new",
        )
        test_featureprop = Featureprop.objects.get(feature=test_feature)
        self.assertEqual("feature new", test_featureprop.value)

        # store the ontology_term
        test_feature_file.store_feature_annotation(
            feature="feat2",
            soterm="polypeptide",
            cvterm="ontology_term",
            annotation="GO:12345",
        )
        test_cvterm = Cvterm.objects.get(name="go test term")
        test_feature_cvterm = FeatureCvterm.objects.get(
            feature=test_feature, cvterm=test_cvterm
        )
        self.assertIsNotNone(test_feature_cvterm)

        # store the dbxref
        test_feature_file.store_feature_annotation(
            feature="feat2",
            soterm="polypeptide",
            cvterm="dbxref",
            annotation="GEO:123456",
        )
        test_db = Db.objects.get(name="GEO")
        test_dbxref = Dbxref.objects.get(db=test_db, accession="123456")
        test_feature_dbxref = FeatureDbxref.objects.get(
            feature=test_feature, dbxref=test_dbxref
        )
        self.assertIsNotNone(test_feature_dbxref)

    def test_store_feature_publication(self):
        """Tests - store feature publication."""
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

        test_db = Db.objects.create(name="SO")
        test_dbxref = Dbxref.objects.create(accession="12345", db=test_db)
        test_cv = Cv.objects.create(name="sequence")
        test_so_term = Cvterm.objects.create(
            name="gene",
            cv=test_cv,
            dbxref=test_dbxref,
            is_obsolete=0,
            is_relationshiptype=0,
        )
        test_dbxref = Dbxref.objects.create(accession="123456", db=test_db)
        Cvterm.objects.create(
            name="polypeptide",
            cv=test_cv,
            dbxref=test_dbxref,
            is_obsolete=0,
            is_relationshiptype=0,
        )
        test_dbxref = Dbxref.objects.create(accession="123455", db=test_db)
        Cvterm.objects.create(
            name="protein_match",
            cv=test_cv,
            dbxref=test_dbxref,
            is_obsolete=0,
            is_relationshiptype=0,
        )

        test_organism = Organism.objects.create(genus="Mus", species="musculus")

        test_db = Db.objects.create(name="GFF_SOURCE")
        test_dbxref = Dbxref.objects.create(accession="feat_gene", db=test_db)
        test_feature = Feature.objects.create(
            organism=test_organism,
            uniquename="feat_gene",
            dbxref=test_dbxref,
            is_analysis=False,
            type_id=test_so_term.cvterm_id,
            is_obsolete=False,
            timeaccessioned=datetime.now(timezone.utc),
            timelastmodified=datetime.now(timezone.utc),
        )

        db2 = BibDatabase()
        db2.entries = [
            {
                "journal": "Nice Journal",
                "comments": "A comment",
                "pages": "12--23",
                "month": "jan",
                "abstract": "This is an abstract. This line should be "
                "long enough to test multilines...",
                "title": "An amazing title",
                "year": "2013",
                "doi": "10.1186/s12864-016-2535-300002",
                "volume": "12",
                "ID": "Teste2018",
                "author": "Foo, b. and Foo1, b. and Foo b.",
                "keyword": "keyword1, keyword2",
                "ENTRYTYPE": "article",
            }
        ]
        for entry in db2.entries:
            bibtest = PublicationLoader()
            bibtest.store_bibtex_entry(entry)

        test_feature_file = FeatureLoader(filename="file.name", source="GFF_loader")

        test_feature_file.store_feature_publication(
            feature="feat_gene", soterm="gene", doi="10.1186/s12864-016-2535-300002"
        )
        test_featurepub = FeaturePub.objects.get(feature=test_feature)
        self.assertEqual("An amazing title", test_featurepub.pub.title)

    def test_store_feature_dbxref(self):
        """Tests - store feature dbxref."""
        # creating exact term
        test_db_global = Db.objects.create(name="_global")
        test_dbxref = Dbxref.objects.create(accession="exact", db=test_db_global)
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

        test_db = Db.objects.create(name="SO")
        test_dbxref = Dbxref.objects.create(accession="12345", db=test_db)
        test_cv = Cv.objects.create(name="sequence")
        test_so_term = Cvterm.objects.create(
            name="polypeptide",
            cv=test_cv,
            dbxref=test_dbxref,
            is_obsolete=0,
            is_relationshiptype=0,
        )
        test_dbxref = Dbxref.objects.create(accession="123455", db=test_db)
        Cvterm.objects.create(
            name="protein_match",
            cv=test_cv,
            dbxref=test_dbxref,
            is_obsolete=0,
            is_relationshiptype=0,
        )

        test_organism = Organism.objects.create(genus="Mus", species="musculus")

        test_db = Db.objects.create(name="GFF_SOURCE")
        test_dbxref = Dbxref.objects.create(accession="feat2", db=test_db)
        test_feature = Feature.objects.create(
            organism=test_organism,
            uniquename="feat2",
            dbxref=test_dbxref,
            is_analysis=False,
            type_id=test_so_term.cvterm_id,
            is_obsolete=False,
            timeaccessioned=datetime.now(timezone.utc),
            timelastmodified=datetime.now(timezone.utc),
        )

        test_feature_file = FeatureLoader(filename="file.name", source="GFF_loader")

        # store the feature annotation
        test_feature_file.store_feature_dbxref(
            feature="feat2", soterm="polypeptide", dbxref="GI:12345"
        )
        test_featuredbxref = FeatureDbxref.objects.get(feature=test_feature)
        self.assertEqual("GI", test_featuredbxref.dbxref.db.name)
        self.assertEqual("12345", test_featuredbxref.dbxref.accession)
