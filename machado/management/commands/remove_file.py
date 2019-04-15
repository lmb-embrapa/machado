# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Remove file."""

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from machado.models import Project, Projectprop, AssayProject
from machado.models import Assay, Assayprop, Analysis, Analysisprop
from machado.models import Biomaterial, Biomaterialprop
from machado.models import Feature, Dbxrefprop


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
        if verbosity > 1:
            self.stdout.write('Features: deleting {} and every '
                              'child record (CASCADE)'
                              .format(name))
        try:
            Feature.objects.filter(
                dbxref__Dbxrefprop_dbxref_Dbxref__value=name).delete()
            Dbxrefprop.objects.filter(value=name).delete()
        except ObjectDoesNotExist:
            raise CommandError(
                'Features: cannot remove {} (not registered)'.format(name))
        # Handling Projects
        if verbosity > 1:
            self.stdout.write('Projects: deleting {} and every '
                              'child record (CASCADE)'
                              .format(name))
        try:
            project_ids = list(Projectprop.objects.filter(
                value=name).values_list('project_id', flat=True))
            AssayProject.objects.filter(project_id__in=project_ids).delete()
            Project.objects.filter(project_id__in=project_ids).delete()
            Projectprop.objects.filter(value=name).delete()
        except ObjectDoesNotExist:
            raise CommandError(
                'Projects: cannot remove {} (not registered)'.format(name))
        # Handling Assay
        if verbosity > 1:
            self.stdout.write('Assay: deleting {} and every '
                              'child record (CASCADE)'
                              .format(name))
        try:
            assay_ids = list(Assayprop.objects.filter(
                value=name).values_list('assay_id', flat=True))
            AssayProject.objects.filter(assay_id__in=assay_ids).delete()
            Assay.objects.filter(assay_id__in=assay_ids).delete()
        except ObjectDoesNotExist:
            raise CommandError(
                'Assays: cannot remove {} (not registered)'.format(name))
        # Handling Biomaterial
        if verbosity > 1:
            self.stdout.write('Biomaterial: deleting {} and every '
                              'child record (CASCADE)'
                              .format(name))
        try:
            biomaterial_ids = list(Biomaterialprop.objects.filter(
                value=name).values_list('biomaterial_id', flat=True))
            Biomaterial.objects.filter(
                biomaterial_id__in=biomaterial_ids).delete()
            Biomaterialprop.objects.filter(value=name).delete()
        except ObjectDoesNotExist:
            raise CommandError(
                'Biomaterials: cannot remove {} (not registered)'.format(name))
        # Handling Analysis
        if verbosity > 1:
            self.stdout.write('Analysis: deleting {} and every '
                              'child record (CASCADE)'
                              .format(name))
        try:
            analysis_ids = list(Analysisprop.objects.filter(
                value=name).values_list('analysis_id', flat=True))
            Analysis.objects.filter(analysis_id__in=analysis_ids).delete()
        except ObjectDoesNotExist:
            raise CommandError(
                'Analysis: cannot remove {} (not registered)'.format(name))
        if verbosity > 0:
            self.stdout.write(self.style.SUCCESS('Done'))
