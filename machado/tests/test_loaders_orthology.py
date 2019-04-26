# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Tests orthology loaders."""

from datetime import datetime, timezone

from django.test import TestCase

from machado.loaders.feature import FeatureLoader
from machado.models import Cv, Cvterm, Organism
from machado.models import Db, Dbxref, Feature
from machado.models import Featureprop


class OrthologyTest(TestCase):
    """Tests Orthology."""

    def test_orthology(self):
        """Tests - __init__."""
        # register multispecies organism
        so_db = Db.objects.create(name="SO")
        so_cv = Cv.objects.create(name="sequence")
        # creating test RO term
        ro_db = Db.objects.create(name="RO")
        ro_cv = Cv.objects.create(name="relationship")
        fo_db = Db.objects.create(name="ORTHOMCL_SOURCE")
        fo_cv = Cv.objects.create(name="feature_property")

        # test_dbxref = Dbxref.objects.create(accession='123456', db=test_db)
        so_dbxref = Dbxref.objects.create(accession="357", db=so_db)
        so_dbxref2 = Dbxref.objects.create(accession="358", db=so_db)
        ro_dbxref = Dbxref.objects.create(accession="658", db=ro_db)
        # creating test SO term
        Cvterm.objects.create(
            name="contained in",
            cv=ro_cv,
            dbxref=ro_dbxref,
            is_obsolete=0,
            is_relationshiptype=1,
        )

        ortho_dbxref = Dbxref.objects.create(accession="ORTHOMCL_SOURCE", db=fo_db)
        term = Cvterm.objects.create(
            name="orthologous group",
            cv=fo_cv,
            dbxref=ortho_dbxref,
            is_obsolete=0,
            is_relationshiptype=0,
        )
        poly_cvterm = Cvterm.objects.create(
            name="polypeptide",
            cv=so_cv,
            dbxref=so_dbxref,
            is_obsolete=0,
            is_relationshiptype=0,
        )
        Cvterm.objects.create(
            name="protein_match",
            cv=so_cv,
            dbxref=so_dbxref2,
            is_obsolete=0,
            is_relationshiptype=0,
        )
        db_null = Db.objects.create(name="null")
        null_dbxref = Dbxref.objects.create(db=db_null, accession="null")
        null_cv = Cv.objects.create(name="null")
        Cvterm.objects.create(
            cv=null_cv,
            name="null",
            definition="",
            dbxref=null_dbxref,
            is_obsolete=0,
            is_relationshiptype=0,
        )
        # need to insert organisms first
        organism1 = Organism.objects.create(
            species="coerulea", genus="Aquilegia", abbreviation="Aco"
        )
        organism2 = Organism.objects.create(
            species="distachyon", genus="Brachypodium", abbreviation="Brd"
        )
        organism3 = Organism.objects.create(
            species="clementina", genus="Citrus", abbreviation="Ccl"
        )
        organism4 = Organism.objects.create(
            species="carota", genus="Dacus", abbreviation="Dca"
        )
        organism5 = Organism.objects.create(
            species="grandis", genus="Eucalyptus", abbreviation="Egr"
        )
        organism6 = Organism.objects.create(
            species="vesca", genus="Fragaria", abbreviation="Fve"
        )
        organism7 = Organism.objects.create(
            species="max", genus="Glycine", abbreviation="Gma"
        )
        organism8 = Organism.objects.create(
            species="fedtschenkoi", genus="Kalanchoe", abbreviation="Kld"
        )
        self.assertTrue(Organism.objects.filter(abbreviation="Aco").exists())
        self.assertTrue(Organism.objects.filter(abbreviation="Brd").exists())
        self.assertTrue(Organism.objects.filter(abbreviation="Ccl").exists())
        self.assertTrue(Organism.objects.filter(abbreviation="Dca").exists())
        self.assertTrue(Organism.objects.filter(abbreviation="Egr").exists())
        self.assertTrue(Organism.objects.filter(abbreviation="Fve").exists())
        self.assertTrue(Organism.objects.filter(abbreviation="Gma").exists())
        self.assertTrue(Organism.objects.filter(abbreviation="Kld").exists())

        # also need to insert Features from fasta file first.
        # inserting: Aqcoe0131s0001.1.v3.1
        db = Db.objects.create(name="FASTA_SOURCE")
        acc1 = "Aqcoe0131s0001.1.v3.1"
        dbxref1 = Dbxref.objects.create(db=db, accession=acc1)
        feature1 = Feature.objects.create(
            dbxref=dbxref1,
            organism=organism1,
            uniquename="Aqcoe0131s0001.1.v3.1",
            type=poly_cvterm,
            is_analysis=False,
            is_obsolete=False,
            timeaccessioned=datetime.now(timezone.utc),
            timelastmodified=datetime.now(timezone.utc),
        )
        self.assertTrue(
            Feature.objects.filter(
                type__cv__name="sequence",
                type__name="polypeptide",
                dbxref__accession=acc1,
                dbxref__db__name="FASTA_SOURCE",
            ).exists()
        )
        # inserting: Bradi0180s00100.1.v3.1; Bradi2g20400.1.v3.1
        acc2 = "Bradi0180s00100.1.v3.1"
        dbxref2 = Dbxref.objects.create(db=db, accession=acc2)
        Feature.objects.create(
            dbxref=dbxref2,
            organism=organism2,
            uniquename="Bradi0180s00100.1.v3.1",
            type=poly_cvterm,
            is_analysis=False,
            is_obsolete=False,
            timeaccessioned=datetime.now(timezone.utc),
            timelastmodified=datetime.now(timezone.utc),
        )
        self.assertTrue(
            Feature.objects.filter(
                type__cv__name="sequence",
                type__name="polypeptide",
                dbxref__accession=acc2,
                dbxref__db__name__in=["GFF_SOURCE", "FASTA_SOURCE"],
            ).exists()
        )
        acc3 = "Bradi2g20400.1.v3.1"
        dbxref3 = Dbxref.objects.create(db=db, accession=acc3)
        Feature.objects.create(
            dbxref=dbxref3,
            organism=organism2,
            uniquename="Bradi2g20400.1.v3.1",
            type=poly_cvterm,
            is_analysis=False,
            is_obsolete=False,
            timeaccessioned=datetime.now(timezone.utc),
            timelastmodified=datetime.now(timezone.utc),
        )
        self.assertTrue(
            Feature.objects.filter(
                type__cv__name="sequence",
                type__name="polypeptide",
                dbxref__accession=acc3,
                dbxref__db__name__in=["GFF_SOURCE", "FASTA_SOURCE"],
            ).exists()
        )
        # inserting: Ciclev10013963m.v1.0; Ciclev10013962m.v1.0;
        # Ciclev10013970m.v1.0
        acc4 = "Ciclev10013963m.v1.0"
        dbxref4 = Dbxref.objects.create(db=db, accession=acc4)
        feature4 = Feature.objects.create(
            dbxref=dbxref4,
            organism=organism3,
            uniquename="Ciclev10013963m.v1.0",
            type=poly_cvterm,
            is_analysis=False,
            is_obsolete=False,
            timeaccessioned=datetime.now(timezone.utc),
            timelastmodified=datetime.now(timezone.utc),
        )
        self.assertTrue(
            Feature.objects.filter(
                type__cv__name="sequence",
                type__name="polypeptide",
                dbxref__accession=acc4,
                dbxref__db__name__in=["GFF_SOURCE", "FASTA_SOURCE"],
            ).exists()
        )
        acc5 = "Ciclev10013962m.v1.0"
        dbxref5 = Dbxref.objects.create(db=db, accession=acc5)
        Feature.objects.create(
            dbxref=dbxref5,
            organism=organism3,
            uniquename="Ciclev10013962m.v1.0",
            type=poly_cvterm,
            is_analysis=False,
            is_obsolete=False,
            timeaccessioned=datetime.now(timezone.utc),
            timelastmodified=datetime.now(timezone.utc),
        )
        self.assertTrue(
            Feature.objects.filter(
                type__cv__name="sequence",
                type__name="polypeptide",
                dbxref__accession=acc5,
                dbxref__db__name__in=["GFF_SOURCE", "FASTA_SOURCE"],
            ).exists()
        )
        acc6 = "Ciclev10013970m.v1.0"
        dbxref6 = Dbxref.objects.create(db=db, accession=acc6)
        Feature.objects.create(
            dbxref=dbxref6,
            organism=organism3,
            uniquename="Ciclev10013970m.v1.0",
            type=poly_cvterm,
            is_analysis=False,
            is_obsolete=False,
            timeaccessioned=datetime.now(timezone.utc),
            timelastmodified=datetime.now(timezone.utc),
        )
        self.assertTrue(
            Feature.objects.filter(
                type__cv__name="sequence",
                type__name="polypeptide",
                dbxref__accession=acc6,
                dbxref__db__name__in=["GFF_SOURCE", "FASTA_SOURCE"],
            ).exists()
        )
        # inserting: DCAR_032182.v1.0.388; DCAR_031986.v1.0.388;
        # DCAR_032223.v1.0.388; DCAR_000323.v1.0.388
        acc7 = "DCAR_032182.v1.0.388"
        dbxref7 = Dbxref.objects.create(db=db, accession=acc7)
        Feature.objects.create(
            dbxref=dbxref7,
            organism=organism4,
            uniquename="DCAR_032182.v1.0.388",
            type=poly_cvterm,
            is_analysis=False,
            is_obsolete=False,
            timeaccessioned=datetime.now(timezone.utc),
            timelastmodified=datetime.now(timezone.utc),
        )
        self.assertTrue(
            Feature.objects.filter(
                type__cv__name="sequence",
                type__name="polypeptide",
                dbxref__accession=acc7,
                dbxref__db__name__in=["GFF_SOURCE", "FASTA_SOURCE"],
            ).exists()
        )
        acc8 = "DCAR_031986.v1.0.388"
        dbxref8 = Dbxref.objects.create(db=db, accession=acc8)
        Feature.objects.create(
            dbxref=dbxref8,
            organism=organism4,
            uniquename="DCAR_031986.v1.0.388",
            type=poly_cvterm,
            is_analysis=False,
            is_obsolete=False,
            timeaccessioned=datetime.now(timezone.utc),
            timelastmodified=datetime.now(timezone.utc),
        )
        self.assertTrue(
            Feature.objects.filter(
                type__cv__name="sequence",
                type__name="polypeptide",
                dbxref__accession=acc8,
                dbxref__db__name__in=["GFF_SOURCE", "FASTA_SOURCE"],
            ).exists()
        )
        acc9 = "DCAR_032223.v1.0.388"
        dbxref9 = Dbxref.objects.create(db=db, accession=acc9)
        feature9 = Feature.objects.create(
            dbxref=dbxref9,
            organism=organism4,
            uniquename="DCAR_032223.v1.0.388",
            type=poly_cvterm,
            is_analysis=False,
            is_obsolete=False,
            timeaccessioned=datetime.now(timezone.utc),
            timelastmodified=datetime.now(timezone.utc),
        )
        self.assertTrue(
            Feature.objects.filter(
                type__cv__name="sequence",
                type__name="polypeptide",
                dbxref__accession=acc9,
                dbxref__db__name__in=["GFF_SOURCE", "FASTA_SOURCE"],
            ).exists()
        )
        acc10 = "DCAR_000323.v1.0.388"
        dbxref10 = Dbxref.objects.create(db=db, accession=acc10)
        feature10 = Feature.objects.create(
            dbxref=dbxref10,
            organism=organism4,
            uniquename="DCAR_000323.v1.0.388",
            type=poly_cvterm,
            is_analysis=False,
            is_obsolete=False,
            timeaccessioned=datetime.now(timezone.utc),
            timelastmodified=datetime.now(timezone.utc),
        )
        self.assertTrue(
            Feature.objects.filter(
                type__cv__name="sequence",
                type__name="polypeptide",
                dbxref__accession=acc10,
                dbxref__db__name__in=["GFF_SOURCE", "FASTA_SOURCE"],
            ).exists()
        )
        # inserting: Eucgr.L02820.1.v2.0
        acc11 = "Eucgr.L02820.1.v2.0"
        dbxref11 = Dbxref.objects.create(db=db, accession=acc11)
        Feature.objects.create(
            dbxref=dbxref11,
            organism=organism5,
            uniquename="Eucgr.L02820.1.v2.0",
            type=poly_cvterm,
            is_analysis=False,
            is_obsolete=False,
            timeaccessioned=datetime.now(timezone.utc),
            timelastmodified=datetime.now(timezone.utc),
        )
        self.assertTrue(
            Feature.objects.filter(
                type__cv__name="sequence",
                type__name="polypeptide",
                dbxref__accession=acc11,
                dbxref__db__name__in=["GFF_SOURCE", "FASTA_SOURCE"],
            ).exists()
        )
        # inserting: mrna13067.1-v1.0-hybrid.v1.1
        acc12 = "mrna13067.1-v1.0-hybrid.v1.1"
        dbxref12 = Dbxref.objects.create(db=db, accession=acc12)
        Feature.objects.create(
            dbxref=dbxref12,
            organism=organism6,
            uniquename="mrna13067.1-v1.0-hybrid.v1.1",
            type=poly_cvterm,
            is_analysis=False,
            is_obsolete=False,
            timeaccessioned=datetime.now(timezone.utc),
            timelastmodified=datetime.now(timezone.utc),
        )
        self.assertTrue(
            Feature.objects.filter(
                type__cv__name="sequence",
                type__name="polypeptide",
                dbxref__accession=acc12,
                dbxref__db__name__in=["GFF_SOURCE", "FASTA_SOURCE"],
            ).exists()
        )
        # inserting: Glyma.10G030500.1.Wm82.a2.v1; Glyma.10G053100.1.Wm82.a2.v1
        acc13 = "Glyma.10G030500.1.Wm82.a2.v1"
        dbxref13 = Dbxref.objects.create(db=db, accession=acc13)
        Feature.objects.create(
            dbxref=dbxref13,
            organism=organism7,
            uniquename="Glyma.10G030500.1.Wm82.a2.v1",
            type_id=poly_cvterm.cvterm_id,
            is_analysis=False,
            is_obsolete=False,
            timeaccessioned=datetime.now(timezone.utc),
            timelastmodified=datetime.now(timezone.utc),
        )
        self.assertTrue(
            Feature.objects.filter(
                type__cv__name="sequence",
                type__name="polypeptide",
                dbxref__accession=acc13,
                dbxref__db__name__in=["GFF_SOURCE", "FASTA_SOURCE"],
            ).exists()
        )
        acc14 = "Glyma.10G053100.1.Wm82.a2.v1"
        dbxref14 = Dbxref.objects.create(db=db, accession=acc14)
        feature14 = Feature.objects.create(
            dbxref=dbxref14,
            organism=organism7,
            uniquename="Glyma.10G053100.1.Wm82.a2.v1",
            type_id=poly_cvterm.cvterm_id,
            is_analysis=False,
            is_obsolete=False,
            timeaccessioned=datetime.now(timezone.utc),
            timelastmodified=datetime.now(timezone.utc),
        )
        self.assertTrue(
            Feature.objects.filter(
                type__cv__name="sequence",
                type__name="polypeptide",
                dbxref__accession=acc14,
                dbxref__db__name__in=["GFF_SOURCE", "FASTA_SOURCE"],
            ).exists()
        )
        acc15 = "Glyma.10G008400.1.Wm82.a2.v1"
        dbxref15 = Dbxref.objects.create(db=db, accession=acc15)
        Feature.objects.create(
            dbxref=dbxref15,
            organism=organism7,
            uniquename="Glyma.10G008400.1.Wm82.a2.v1",
            type_id=poly_cvterm.cvterm_id,
            is_analysis=False,
            is_obsolete=False,
            timeaccessioned=datetime.now(timezone.utc),
            timelastmodified=datetime.now(timezone.utc),
        )
        self.assertTrue(
            Feature.objects.filter(
                type__cv__name="sequence",
                type__name="polypeptide",
                dbxref__accession=acc15,
                dbxref__db__name__in=["GFF_SOURCE", "FASTA_SOURCE"],
            ).exists()
        )
        # inserting: Kaladp0598s0001.1.v1.1
        acc16 = "Kaladp0598s0001.1.v1.1"
        dbxref16 = Dbxref.objects.create(db=db, accession=acc16)
        feature16 = Feature.objects.create(
            dbxref=dbxref16,
            organism=organism8,
            uniquename="Kaladp0598s0001.1.v1.1",
            type_id=poly_cvterm.cvterm_id,
            is_analysis=False,
            is_obsolete=False,
            timeaccessioned=datetime.now(timezone.utc),
            timelastmodified=datetime.now(timezone.utc),
        )
        self.assertTrue(
            Feature.objects.filter(
                type__cv__name="sequence",
                type__name="polypeptide",
                dbxref__accession=acc16,
                dbxref__db__name__in=["GFF_SOURCE", "FASTA_SOURCE"],
            ).exists()
        )
        acc17 = "Kaladp0598s0002.1.v1.1"
        dbxref17 = Dbxref.objects.create(db=db, accession=acc17)
        feature17 = Feature.objects.create(
            dbxref=dbxref17,
            organism=organism8,
            uniquename="Kaladp0598s0002.1.v1.1",
            type_id=poly_cvterm.cvterm_id,
            is_analysis=False,
            is_obsolete=False,
            timeaccessioned=datetime.now(timezone.utc),
            timelastmodified=datetime.now(timezone.utc),
        )
        self.assertTrue(
            Feature.objects.filter(
                type__cv__name="sequence",
                type__name="polypeptide",
                dbxref__accession=acc17,
                dbxref__db__name__in=["GFF_SOURCE", "FASTA_SOURCE"],
            ).exists()
        )
        # ########################
        # store feature groups:
        filename = "groups.txt"
        organism, created = Organism.objects.get_or_create(
            abbreviation="multispecies",
            genus="multispecies",
            species="multispecies",
            common_name="multispecies",
        )
        source = "null"
        soterm = "polypeptide"
        test_orthology_loader = FeatureLoader(source=source, filename=filename)
        # ####################
        # test store groups
        group1_name = "machado0001"
        members1 = [
            "Aqcoe0131s0001.1.v3.1",
            "Bradi0180s00100.1.v3.1",
            "Bradi2g20400.1.v3.1",
            "Ciclev10013963m.v1.0",
            "DCAR_032223.v1.0.388",
            "UnknownProtein.v1.1",
        ]
        test_orthology_loader.store_feature_groups(
            group=members1, soterm=soterm, term=term, value=group1_name
        )
        group2_name = "machado0002"
        members2 = [
            "Eucgr.L02820.1.v2.0",
            "mrna13067.1-v1.0-hybrid.v1.1",
            "Ciclev10013970m.v1.0",
            "DCAR_031986.v1.0.388",
        ]
        test_orthology_loader.store_feature_groups(
            group=members2, soterm=soterm, term=term, value=group2_name
        )
        group3_name = "machado0003"
        members3 = [
            "Glyma.10G030500.1.Wm82.a2.v1",
            "Glyma.10G053100.1.Wm82.a2.v1",
            "DCAR_032182.v1.0.388",
        ]
        test_orthology_loader.store_feature_groups(
            group=members3, soterm=soterm, term=term, value=group3_name
        )
        group4_name = "machado0004"
        members4 = ["Glyma.10G008400.1.Wm82.a2.v1", "", "UnknownProtein.v1.2"]
        test_orthology_loader.store_feature_groups(
            group=members4, soterm=soterm, term=term, value=group4_name
        )
        group5_name = "machado0005"
        members5 = ["DCAR_000323.v1.0.388", "Kaladp0598s0002.1.v1.1"]
        test_orthology_loader.store_feature_groups(
            group=members5, soterm=soterm, term=term, value=group5_name
        )
        group6_name = "machado0006"
        members6 = ["Kaladp0598s0001.1.v1.1", "UnknownProtein.v1.3"]
        test_orthology_loader.store_feature_groups(
            group=members6, soterm=soterm, term=term, value=group6_name
        )
        group7_name = "machado0007"
        members7 = ["UnknownProtein.v1.4"]
        test_orthology_loader.store_feature_groups(
            group=members7, soterm=soterm, term=term, value=group7_name
        )

        # ###check if relationships exist###
        # in a group (machado0001 and machado0005)
        self.assertTrue(
            Featureprop.objects.filter(
                feature_id=feature1.feature_id, type_id=term, value=group1_name
            ).exists()
        )
        self.assertTrue(
            Featureprop.objects.filter(
                feature_id=feature9.feature_id, type_id=term, value=group1_name
            ).exists()
        )
        self.assertTrue(
            Featureprop.objects.filter(
                feature_id=feature4.feature_id, type_id=term, value=group1_name
            ).exists()
        )
        # another example group5
        self.assertTrue(
            Featureprop.objects.filter(
                feature_id=feature10.feature_id, type_id=term, value=group5_name
            ).exists()
        )
        self.assertTrue(
            Featureprop.objects.filter(
                feature_id=feature17.feature_id, type_id=term, value=group5_name
            ).exists()
        )
        # another example:
        # ###check if a relationship does not exist###
        # between features from different groups (machado0004 and machado0003)
        self.assertFalse(
            Featureprop.objects.filter(
                feature_id=feature16.feature_id, type_id=term, value=group6_name
            ).exists()
        )
        self.assertFalse(
            Featureprop.objects.filter(
                feature_id=feature4.feature_id, type_id=term, value=group2_name
            ).exists()
        )
        self.assertFalse(
            Featureprop.objects.filter(
                feature_id=feature14.feature_id, type_id=term, value=group1_name
            ).exists()
        )
