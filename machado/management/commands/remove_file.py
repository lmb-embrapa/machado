# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Remove file."""

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from machado.models import Dbxref, Dbxrefprop
from machado.models import Project, Projectprop
from machado.models import Biomaterial, Biomaterialprop
from machado.models import Assay, Assayprop, AssayProject
from machado.models import Analysis, Analysisprop
from machado.models import Feature, Featureloc, FeatureDbxref
from machado.models import Featureprop, FeatureRelationship, FeatureSynonym
from machado.models import FeatureCvterm
from tqdm import tqdm


class Command(BaseCommand):
    """Remove file."""

    help = 'Remove file (CASCADE)'

    def add_arguments(self, parser):
        """Define the arguments."""
        parser.add_argument(
            "--name", help="File name", required=True, type=str)

    def handle(self,
               name: str,
               verbosity: int = 0,
               **options):
        """Execute the main function."""
        # Handling Features
        project_ids = list()
        feature_ids = list()
        dbxref_ids = list()
        assay_ids = list()
        biomaterial_ids = list()
        try:
            dbxref_ids = list(Dbxrefprop.objects.filter(
                value=name).values_list('dbxref_id', flat=True))
            feature_ids = list(Feature.objects.filter(
                dbxref_id__in=dbxref_ids).values_list('feature_id', flat=True))
            if verbosity > 0:
                self.stdout.write('Features: deleting {} and every '
                                  'child record (CASCADE)'
                                  .format(name))
                for fid in tqdm(feature_ids, total=len(feature_ids)):
                    Featureloc.objects.filter(feature_id=fid).delete()
                    Featureprop.objects.filter(feature_id=fid).delete()
                    FeatureSynonym.objects.filter(feature_id=fid).delete()
                    FeatureCvterm.objects.filter(feature_id=fid).delete()
                    FeatureDbxref.objects.filter(feature_id=fid).delete()
                    FeatureRelationship.objects.filter(object_id=fid).delete()
                    FeatureRelationship.objects.filter(subject_id=fid).delete()
                    Feature.objects.filter(feature_id=fid).delete()
                Dbxrefprop.objects.filter(value=name).delete()
                for dbxrfid in tqdm(dbxref_ids, total=len(dbxref_ids)):
                    Dbxref.objects.filter(dbxref_id=dbxrfid).delete()
            else:
                for fid in feature_ids:
                    Featureloc.objects.filter(feature_id=fid).delete()
                    Featureprop.objects.filter(feature_id=fid).delete()
                    FeatureSynonym.objects.filter(feature_id=fid).delete()
                    FeatureCvterm.objects.filter(feature_id=fid).delete()
                    FeatureDbxref.objects.filter(feature_id=fid).delete()
                    FeatureRelationship.objects.filter(object_id=fid).delete()
                    FeatureRelationship.objects.filter(subject_id=fid).delete()
                    Feature.objects.filter(feature_id=fid).delete()
                Dbxrefprop.objects.filter(value=name).delete()
                for dbxrfid in dbxref_ids:
                    Dbxref.objects.filter(dbxref_id=dbxrfid).delete()
        except ObjectDoesNotExist:
            raise CommandError(
                'Features: cannot remove {} (not registered)'.format(name))
        # Handling Projects
        try:
            project_ids = list(Projectprop.objects.filter(
                value=name).values_list('project_id', flat=True))
            if verbosity > 0:
                self.stdout.write('Projects: deleting {} and every '
                                  'child record (CASCADE)'
                                  .format(name))
                for pid in tqdm(project_ids, total=len(project_ids)):
                    AssayProject.objects.filter(project_id=pid).delete()
                    Project.objects.filter(project_id=pid).delete()
            else:
                for pid in project_ids:
                    AssayProject.objects.filter(project_id=pid).delete()
                    Project.objects.filter(project_id=pid).delete()
        except ObjectDoesNotExist:
            raise CommandError(
                'Projects: cannot remove {} (not registered)'.format(name))
        # Handling Biomaterial
        try:
            biomaterial_ids = list(Biomaterialprop.objects.filter(
                value=name).values_list('biomaterial_id', flat=True))
            if verbosity > 0:
                self.stdout.write('Biomaterials: deleting {} and every '
                                  'child record (CASCADE)'
                                  .format(name))
                for bid in tqdm(biomaterial_ids, total=len(biomaterial_ids)):
                    Biomaterial.objects.filter(biomaterial_id=bid).delete()
            else:
                for bid in biomaterial_ids:
                    Biomaterial.objects.filter(biomaterial_id=bid).delete()

        except ObjectDoesNotExist:
            raise CommandError(
                'Biomaterials: cannot remove {} (not registered)'.format(name))
        # Handling Assay
        try:
            assay_ids = list(Assayprop.objects.filter(
                value=name).values_list('assay_id', flat=True))
            if verbosity > 0:
                self.stdout.write('Assays: deleting {} and every '
                                  'child record (CASCADE)'
                                  .format(name))
                for aid in tqdm(assay_ids, total=len(assay_ids)):
                    AssayProject.objects.filter(assay_id=aid).delete()
                    Assay.objects.filter(assay_id=aid).delete()
            else:
                for aid in assay_ids:
                    AssayProject.objects.filter(assay_id=aid).delete()
                    Assay.objects.filter(assay_id=aid).delete()
        except ObjectDoesNotExist:
            raise CommandError(
                'Assays: cannot remove {} (not registered)'.format(name))
        # Handling Analysis
        try:
            analysis_ids = list(Analysisprop.objects.filter(
                value=name).values_list('analysis_id', flat=True))
            if verbosity > 0:
                self.stdout.write('Analysis: deleting {} and every '
                                  'child record (CASCADE)'
                                  .format(name))
                for anid in tqdm(analysis_ids, total=len(analysis_ids)):
                    Analysis.objects.filter(analysis_id=anid).delete()
            else:
                for anid in analysis_ids:
                    Analysis.objects.filter(analysis_id=anid).delete()
        except ObjectDoesNotExist:
            raise CommandError(
                'Analysis: cannot remove {} (not registered)'.format(name))
        if verbosity > 0:
            self.stdout.write(self.style.SUCCESS('Done'))
