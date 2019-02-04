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
from machado.models import Feature, Featureloc, FeatureDbxref
from machado.models import Featureprop, FeatureRelationship, FeatureSynonym
from machado.models import FeatureCvterm


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
            if verbosity > 0:
                self.stdout.write('Features: deleting {} and every '
                                  'child record (CASCADE)'
                                  .format(name))
            dbxref_ids = list(Dbxrefprop.objects.filter(
                value=name).values_list('dbxref_id', flat=True))
            feature_ids = list(Feature.objects.filter(
                dbxref_id__in=dbxref_ids).values_list('feature_id', flat=True))
            Featureloc.objects.filter(feature_id__in=feature_ids).delete()
            Featureprop.objects.filter(feature_id__in=feature_ids).delete()
            FeatureSynonym.objects.filter(feature_id__in=feature_ids).delete()
            FeatureCvterm.objects.filter(feature_id__in=feature_ids).delete()
            FeatureDbxref.objects.filter(feature_id__in=feature_ids).delete()
            FeatureRelationship.objects.filter(
                object_id__in=feature_ids).delete()
            FeatureRelationship.objects.filter(
                subject_id__in=feature_ids).delete()
            Feature.objects.filter(dbxref_id__in=dbxref_ids).delete()
            Dbxrefprop.objects.filter(value=name).delete()
            Dbxref.objects.filter(dbxref_id__in=dbxref_ids).delete()
            if verbosity > 0:
                self.stdout.write(self.style.SUCCESS('Done'))
        except ObjectDoesNotExist:
            raise CommandError(
                'Features: cannot remove {} (not registered)'.format(name))
        # Handling Projects
        try:
            if verbosity > 0:
                self.stdout.write('Projects: deleting {} and every '
                                  'child record (CASCADE)'
                                  .format(name))
            project_ids = list(Projectprop.objects.filter(
                value=name).values_list('project_id', flat=True))
            AssayProject.objects.filter(
                project_id__in=project_ids).delete()
            Project.objects.filter(project_id__in=project_ids).delete()
            if verbosity > 0:
                self.stdout.write(self.style.SUCCESS('Done'))
        except ObjectDoesNotExist:
            raise CommandError(
                'Projects: cannot remove {} (not registered)'.format(name))
        # Handling Biomaterial
        try:
            if verbosity > 0:
                self.stdout.write('Biomaterials: deleting {} and every '
                                  'child record (CASCADE)'
                                  .format(name))
            biomaterial_ids = list(Biomaterialprop.objects.filter(
                value=name).values_list('biomaterial_id', flat=True))
            Biomaterial.objects.filter(
                biomaterial_id__in=biomaterial_ids).delete()
            if verbosity > 0:
                self.stdout.write(self.style.SUCCESS('Done'))
        except ObjectDoesNotExist:
            raise CommandError(
                'Biomaterials: cannot remove {} (not registered)'.format(name))
        # Handling Assay
        try:
            if verbosity > 0:
                self.stdout.write('Assays: deleting {} and every '
                                  'child record (CASCADE)'
                                  .format(name))
            assay_ids = list(Assayprop.objects.filter(
                value=name).values_list('assay_id', flat=True))
            Assay.objects.filter(
                assay_id__in=assay_ids).delete()
            AssayProject.objects.filter(
                assay_id__in=assay_ids).delete()
            if verbosity > 0:
                self.stdout.write(self.style.SUCCESS('Done'))
        except ObjectDoesNotExist:
            raise CommandError(
                'Assays: cannot remove {} (not registered)'.format(name))
