# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Tests orthology loaders."""

from machado.models import Cv, Cvterm, Organism
from machado.models import Db, Dbxref, Feature
from machado.models import FeatureRelationship, FeatureRelationshipprop
from machado.loaders.orthology import OrthologyLoader
from django.core.management import call_command
from django.test import TestCase
from datetime import datetime, timezone


class OrthologyTest(TestCase):
    """Tests Orthology."""

    def test_orthology(self):
        """Tests - __init__."""
        filename = 'groups.txt'
        # global_db = Db.objects.create(name='_global')
        so_db = Db.objects.create(name='SO')
        ro_db = Db.objects.create(name='RO')
        Db.objects.create(name='FASTA_source')
        so_dbxref = Dbxref.objects.create(accession='00001', db=so_db)
        so2_dbxref = Dbxref.objects.create(accession='00002', db=so_db)
        # so3_dbxref = Dbxref.objects.create(accession='00003', db=so_db)
        sequence_cv = Cv.objects.create(
                name='sequence',
                definition="so-xp/releases/2015-11-24/so-xp.owl")
        Cvterm.objects.create(
                name='assembly',
                cv=sequence_cv, dbxref=so_dbxref, is_obsolete=0,
                is_relationshiptype=0)
        Cvterm.objects.create(
                name='protein_match',
                cv=sequence_cv, dbxref=so2_dbxref, is_obsolete=0,
                is_relationshiptype=0)
        # Cvterm.objects.create(
        #         name='mRNA',
        #         cv=sequence_cv, dbxref=so2_dbxref, is_obsolete=0,
        #         is_relationshiptype=0)
        ro_dbxref = Dbxref.objects.create(accession='00003', db=ro_db)
        ro_cv = Cv.objects.create(name='relationship')
        cvterm_contained_in = Cvterm.objects.create(
            name='contained in', cv=ro_cv, dbxref=ro_dbxref,
            is_obsolete=0, is_relationshiptype=1)
        ortho_dbxref = Dbxref.objects.create(
                accession='in orthology relationship with',
                db=ro_db)
        poly_dbxref = Dbxref.objects.create(
                accession='0000104',
                db=so_db)
        Cvterm.objects.create(
                name='in orthology relationship with', cv=ro_cv,
                dbxref=ortho_dbxref, is_obsolete=0,
                is_relationshiptype=1)
        poly_cvterm = Cvterm.objects.create(
                name='polypeptide', cv=sequence_cv,
                dbxref=poly_dbxref,
                is_obsolete=0, is_relationshiptype=0)
        # need to insert organisms first
        organism1 = Organism.objects.create(species="coerulea",
                                            genus="Aquilegia",
                                            abbreviation='Aco')
        organism2 = Organism.objects.create(species="distachyon",
                                            genus="Brachypodium",
                                            abbreviation='Brd')
        organism3 = Organism.objects.create(species="clementina",
                                            genus="Citrus",
                                            abbreviation='Ccl')
        organism4 = Organism.objects.create(species="carota",
                                            genus="Dacus",
                                            abbreviation='Dca')
        organism5 = Organism.objects.create(species="grandis",
                                            genus="Eucalyptus",
                                            abbreviation='Egr')
        organism6 = Organism.objects.create(species="vesca",
                                            genus="Fragaria",
                                            abbreviation='Fve')
        organism7 = Organism.objects.create(species="max",
                                            genus="Glycine",
                                            abbreviation='Gma')
        organism8 = Organism.objects.create(species="fedtschenkoi",
                                            genus="Kalanchoe",
                                            abbreviation='Kld')
        self.assertTrue(Organism.objects.filter(abbreviation='Aco').exists())
        self.assertTrue(Organism.objects.filter(abbreviation='Brd').exists())
        self.assertTrue(Organism.objects.filter(abbreviation='Ccl').exists())
        self.assertTrue(Organism.objects.filter(abbreviation='Dca').exists())
        self.assertTrue(Organism.objects.filter(abbreviation='Egr').exists())
        self.assertTrue(Organism.objects.filter(abbreviation='Fve').exists())
        self.assertTrue(Organism.objects.filter(abbreviation='Gma').exists())
        self.assertTrue(Organism.objects.filter(abbreviation='Kld').exists())

        # also need to insert Features from fasta file first.
        # inserting: Aqcoe0131s0001.1.v3.1
        feature1 = Feature.objects.create(
                              dbxref=poly_dbxref,
                              organism=organism1,
                              uniquename="Aqcoe0131s0001.1.v3.1",
                              type_id=poly_cvterm.cvterm_id,
                              is_analysis=False,
                              is_obsolete=False,
                              timeaccessioned=datetime.
                              now(timezone.utc),
                              timelastmodified=datetime.
                              now(timezone.utc))
        self.assertTrue(Feature.objects.filter(
                                  uniquename='Aqcoe0131s0001.1.v3.1').exists())
        # inserting: Bradi0180s00100.1.v3.1; Bradi2g20400.1.v3.1
        Feature.objects.create(
                              dbxref=poly_dbxref,
                              organism=organism2,
                              uniquename="Bradi0180s00100.1.v3.1",
                              type_id=poly_cvterm.cvterm_id,
                              is_analysis=False,
                              is_obsolete=False,
                              timeaccessioned=datetime.
                              now(timezone.utc),
                              timelastmodified=datetime.
                              now(timezone.utc))
        Feature.objects.create(
                              dbxref=poly_dbxref,
                              organism=organism2,
                              uniquename="Bradi2g20400.1.v3.1",
                              type_id=poly_cvterm.cvterm_id,
                              is_analysis=False,
                              is_obsolete=False,
                              timeaccessioned=datetime.
                              now(timezone.utc),
                              timelastmodified=datetime.
                              now(timezone.utc))
        self.assertTrue(Feature.objects.filter(
                                 uniquename='Bradi0180s00100.1.v3.1').exists())
        self.assertTrue(Feature.objects.filter(
                                 uniquename='Bradi2g20400.1.v3.1').exists())
        # inserting: Ciclev10013963m.v1.0; Ciclev10013962m.v1.0;
        # Ciclev10013970m.v1.0
        feature4 = Feature.objects.create(
                              dbxref=poly_dbxref,
                              organism=organism3,
                              uniquename="Ciclev10013963m.v1.0",
                              type_id=poly_cvterm.cvterm_id,
                              is_analysis=False,
                              is_obsolete=False,
                              timeaccessioned=datetime.
                              now(timezone.utc),
                              timelastmodified=datetime.
                              now(timezone.utc))
        Feature.objects.create(
                              dbxref=poly_dbxref,
                              organism=organism3,
                              uniquename="Ciclev10013962m.v1.0",
                              type_id=poly_cvterm.cvterm_id,
                              is_analysis=False,
                              is_obsolete=False,
                              timeaccessioned=datetime.
                              now(timezone.utc),
                              timelastmodified=datetime.
                              now(timezone.utc))
        Feature.objects.create(
                              dbxref=poly_dbxref,
                              organism=organism3,
                              uniquename="Ciclev10013970m.v1.0",
                              type_id=poly_cvterm.cvterm_id,
                              is_analysis=False,
                              is_obsolete=False,
                              timeaccessioned=datetime.
                              now(timezone.utc),
                              timelastmodified=datetime.
                              now(timezone.utc))
        self.assertTrue(Feature.objects.filter(
                                 uniquename='Ciclev10013963m.v1.0').exists())
        self.assertTrue(Feature.objects.filter(
                                 uniquename='Ciclev10013962m.v1.0').exists())
        self.assertTrue(Feature.objects.filter(
                                 uniquename='Ciclev10013970m.v1.0').exists())
        # inserting: DCAR_032182.v1.0.388; DCAR_031986.v1.0.388;
        # DCAR_032223.v1.0.388; DCAR_000323.v1.0.388
        Feature.objects.create(
                              dbxref=poly_dbxref,
                              organism=organism4,
                              uniquename="DCAR_032182.v1.0.388",
                              type_id=poly_cvterm.cvterm_id,
                              is_analysis=False,
                              is_obsolete=False,
                              timeaccessioned=datetime.
                              now(timezone.utc),
                              timelastmodified=datetime.
                              now(timezone.utc))
        Feature.objects.create(
                              dbxref=poly_dbxref,
                              organism=organism4,
                              uniquename="DCAR_031986.v1.0.388",
                              type_id=poly_cvterm.cvterm_id,
                              is_analysis=False,
                              is_obsolete=False,
                              timeaccessioned=datetime.
                              now(timezone.utc),
                              timelastmodified=datetime.
                              now(timezone.utc))
        feature9 = Feature.objects.create(
                              dbxref=poly_dbxref,
                              organism=organism4,
                              uniquename="DCAR_032223.v1.0.388",
                              type_id=poly_cvterm.cvterm_id,
                              is_analysis=False,
                              is_obsolete=False,
                              timeaccessioned=datetime.
                              now(timezone.utc),
                              timelastmodified=datetime.
                              now(timezone.utc))
        feature10 = Feature.objects.create(
                              dbxref=poly_dbxref,
                              organism=organism4,
                              uniquename="DCAR_000323.v1.0.388",
                              type_id=poly_cvterm.cvterm_id,
                              is_analysis=False,
                              is_obsolete=False,
                              timeaccessioned=datetime.
                              now(timezone.utc),
                              timelastmodified=datetime.
                              now(timezone.utc))
        self.assertTrue(Feature.objects.filter(
                                 uniquename='DCAR_032182.v1.0.388').exists())
        self.assertTrue(Feature.objects.filter(
                                 uniquename='DCAR_031986.v1.0.388').exists())
        self.assertTrue(Feature.objects.filter(
                                 uniquename='DCAR_032223.v1.0.388').exists())
        self.assertTrue(Feature.objects.filter(
                                 uniquename='DCAR_000323.v1.0.388').exists())
        # inserting: Eucgr.L02820.1.v2.0
        Feature.objects.create(
                              dbxref=poly_dbxref,
                              organism=organism5,
                              uniquename="Eucgr.L02820.1.v2.0",
                              type_id=poly_cvterm.cvterm_id,
                              is_analysis=False,
                              is_obsolete=False,
                              timeaccessioned=datetime.
                              now(timezone.utc),
                              timelastmodified=datetime.
                              now(timezone.utc))
        self.assertTrue(Feature.objects.filter(
                                 uniquename='Eucgr.L02820.1.v2.0').exists())
        # inserting: mrna13067.1-v1.0-hybrid.v1.1
        Feature.objects.create(
                              dbxref=poly_dbxref,
                              organism=organism6,
                              uniquename="mrna13067.1-v1.0-hybrid.v1.1",
                              type_id=poly_cvterm.cvterm_id,
                              is_analysis=False,
                              is_obsolete=False,
                              timeaccessioned=datetime.
                              now(timezone.utc),
                              timelastmodified=datetime.
                              now(timezone.utc))
        self.assertTrue(Feature.objects.filter(
                           uniquename='mrna13067.1-v1.0-hybrid.v1.1').exists())
        # inserting: Glyma.10G030500.1.Wm82.a2.v1; Glyma.10G053100.1.Wm82.a2.v1
        # Glyma.10G008400.1.Wm82.a2.v1
        Feature.objects.create(
                              dbxref=poly_dbxref,
                              organism=organism7,
                              uniquename="Glyma.10G030500.1.Wm82.a2.v1",
                              type_id=poly_cvterm.cvterm_id,
                              is_analysis=False,
                              is_obsolete=False,
                              timeaccessioned=datetime.
                              now(timezone.utc),
                              timelastmodified=datetime.
                              now(timezone.utc))
        feature14 = Feature.objects.create(
                              dbxref=poly_dbxref,
                              organism=organism7,
                              uniquename="Glyma.10G053100.1.Wm82.a2.v1",
                              type_id=poly_cvterm.cvterm_id,
                              is_analysis=False,
                              is_obsolete=False,
                              timeaccessioned=datetime.
                              now(timezone.utc),
                              timelastmodified=datetime.
                              now(timezone.utc))
        Feature.objects.create(
                              dbxref=poly_dbxref,
                              organism=organism7,
                              uniquename="Glyma.10G008400.1.Wm82.a2.v1",
                              type_id=poly_cvterm.cvterm_id,
                              is_analysis=False,
                              is_obsolete=False,
                              timeaccessioned=datetime.
                              now(timezone.utc),
                              timelastmodified=datetime.
                              now(timezone.utc))
        self.assertTrue(Feature.objects.filter(
                           uniquename='Glyma.10G030500.1.Wm82.a2.v1').exists())
        self.assertTrue(Feature.objects.filter(
                           uniquename='Glyma.10G053100.1.Wm82.a2.v1').exists())
        self.assertTrue(Feature.objects.filter(
                           uniquename='Glyma.10G008400.1.Wm82.a2.v1').exists())
        # inserting: Kaladp0598s0001.1.v1.1
        feature16 = Feature.objects.create(
                              dbxref=poly_dbxref,
                              organism=organism8,
                              uniquename="Kaladp0598s0001.1.v1.1",
                              type_id=poly_cvterm.cvterm_id,
                              is_analysis=False,
                              is_obsolete=False,
                              timeaccessioned=datetime.
                              now(timezone.utc),
                              timelastmodified=datetime.
                              now(timezone.utc))
        feature17 = Feature.objects.create(
                              dbxref=poly_dbxref,
                              organism=organism8,
                              uniquename="Kaladp0598s0002.1.v1.1",
                              type_id=poly_cvterm.cvterm_id,
                              is_analysis=False,
                              is_obsolete=False,
                              timeaccessioned=datetime.
                              now(timezone.utc),
                              timelastmodified=datetime.
                              now(timezone.utc))
        self.assertTrue(Feature.objects.filter(
                           uniquename='Kaladp0598s0001.1.v1.1').exists())
        self.assertTrue(Feature.objects.filter(
                           uniquename='Kaladp0598s0002.1.v1.1').exists())
        # store orthologous groups:
        group1 = OrthologyLoader('machado0001', filename)
        members1 = ['Aqcoe0131s0001.1.v3.1', 'Bradi0180s00100.1.v3.1',
                    'Bradi2g20400.1.v3.1', 'Ciclev10013963m.v1.0',
                    'DCAR_032223.v1.0.388', 'UnknownProtein.v1.1']
        group1.store_orthologous_group(members1)
        group2 = OrthologyLoader('machado0002', filename)
        members2 = ['Eucgr.L02820.1.v2.0',
                    'mrna13067.1-v1.0-hybrid.v1.1', 'Ciclev10013970m.v1.0',
                    'DCAR_031986.v1.0.388']
        group2.store_orthologous_group(members2)
        group3 = OrthologyLoader('machado0003', filename)
        members3 = ['Glyma.10G030500.1.Wm82.a2.v1',
                    'Glyma.10G053100.1.Wm82.a2.v1', 'DCAR_032182.v1.0.388']
        group3.store_orthologous_group(members3)
        group4 = OrthologyLoader('machado0004', filename)
        members4 = ['Glyma.10G008400.1.Wm82.a2.v1',
                    'Ciclev10013963m.v1.0', 'UnknownProtein.v1.2']
        group4.store_orthologous_group(members4)
        group5 = OrthologyLoader('machado0005', filename)
        members5 = ['DCAR_000323.v1.0.388', 'Kaladp0598s0002.1.v1.1']
        group5.store_orthologous_group(members5)
        group6 = OrthologyLoader('machado0006', filename)
        members6 = ['Kaladp0598s0001.1.v1.1', 'UnknownProtein.v1.3']
        group6.store_orthologous_group(members6)
        group7 = OrthologyLoader('machado0007', filename)
        members7 = ['UnknownProtein.v1.4']
        group7.store_orthologous_group(members7)

        # ###check if relationships exist###
        # in a group (machado0001 and machado0005)
        self.assertTrue(FeatureRelationship.objects.filter(
                           subject_id=feature9.feature_id,
                           object_id=feature1.feature_id).exists())
        frelationship9 = FeatureRelationship.objects.get(
                           subject_id=feature9.feature_id,
                           object_id=feature1.feature_id)
        self.assertTrue(FeatureRelationshipprop.objects.filter(
                           feature_relationship=frelationship9,
                           type_id=cvterm_contained_in.cvterm_id,
                           value=filename,
                           rank=0).exists())
        # same but in reverse
        self.assertTrue(FeatureRelationship.objects.filter(
                           subject_id=feature1.feature_id,
                           object_id=feature9.feature_id).exists())
        frelationship1 = FeatureRelationship.objects.get(
                           subject_id=feature1.feature_id,
                           object_id=feature9.feature_id)
        self.assertTrue(FeatureRelationshipprop.objects.filter(
                           feature_relationship=frelationship1,
                           type_id=cvterm_contained_in.cvterm_id,
                           value=filename,
                           rank=0).exists())
        # another example:
        self.assertTrue(FeatureRelationship.objects.filter(
                           subject_id=feature10.feature_id,
                           object_id=feature17.feature_id).exists())
        frelationship10 = FeatureRelationship.objects.get(
                           subject_id=feature10.feature_id,
                           object_id=feature17.feature_id)
        self.assertTrue(FeatureRelationshipprop.objects.filter(
                           feature_relationship=frelationship10,
                           type_id=cvterm_contained_in.cvterm_id,
                           value=filename,
                           rank=0).exists())
        # another example:
        # ###check if a relationship does not exist###
        # between features from different groups (machado0004 and machado0003)
        self.assertFalse(FeatureRelationship.objects.filter(
                           subject_id=feature4.feature_id,
                           object_id=feature14.feature_id).exists())
        # in orphaned groups (machado0006)
        self.assertFalse(FeatureRelationship.objects.filter(
                           subject_id=feature16.feature_id).exists())
        # removing all relationships
        call_command("remove_relationship",
                     "--file=groups.txt",
                     "--verbosity=0")
        self.assertFalse(FeatureRelationship.objects.filter(
                           subject_id=feature9.feature_id,
                           object_id=feature1.feature_id).exists())
        self.assertFalse(FeatureRelationship.objects.filter(
                           subject_id=feature1.feature_id,
                           object_id=feature9.feature_id).exists())
        self.assertFalse(FeatureRelationship.objects.filter(
                           subject_id=feature10.feature_id,
                           object_id=feature17.feature_id).exists())
        self.assertFalse(FeatureRelationshipprop.objects.filter(
                           feature_relationship=frelationship9,
                           type_id=cvterm_contained_in.cvterm_id,
                           value=filename,
                           rank=0).exists())
        self.assertFalse(FeatureRelationshipprop.objects.filter(
                           feature_relationship=frelationship1,
                           type_id=cvterm_contained_in.cvterm_id,
                           value=filename,
                           rank=0).exists())
        self.assertFalse(FeatureRelationshipprop.objects.filter(
                           feature_relationship=frelationship10,
                           type_id=cvterm_contained_in.cvterm_id,
                           value=filename,
                           rank=0).exists())
