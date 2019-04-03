# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Remove relationship."""

from machado.models import Cvterm, FeatureRelationship, FeatureRelationshipprop
from machado.loaders.exceptions import ImportingError
from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import os


class Command(BaseCommand):
    """Remove relationship."""

    help = 'Remove relationship'

    def add_arguments(self, parser):
        """Define the arguments."""
        parser.add_argument("--file",
                            help="name of the file (e.g.: groups.txt",
                            required=True,
                            type=str)
        parser.add_argument("--cpu",
                            help="Number of threads",
                            required=False,
                            type=int)

    def remove_fr(self,
                  fr_id: str):
        try:
            FeatureRelationship.objects.filter(
                   feature_relationship_id=fr_id
                   ).delete()
        except Exception as e:
            raise(e)

    def handle(self,
               file: str,
               cpu: int = 0,
               verbosity: int = 0,
               **options):
        """Execute the main function."""
        # get cvterm for contained in
        try:
            cvterm_contained_in = Cvterm.objects.get(
                name='contained in', cv__name='relationship')
        except IntegrityError as e:
            raise ImportingError(e)
        filename = os.path.basename(file)
        if cpu:
            try:
                tasks = list()
                pool = ThreadPoolExecutor(max_workers=cpu)
                frps = FeatureRelationshipprop.objects.filter(
                        value=filename,
                        type_id=cvterm_contained_in.cvterm_id)
                if verbosity > 0:
                    self.stdout.write(
                        'Preprocessing (using {} cpu)...'.format(cpu))
                    for frp in tqdm(frps, total=len(frps)):
                        tasks.append(pool.submit(
                                  self.remove_fr,
                                  frp=frp.feature_relationship_id,
                                  ))
                else:
                    for frp in frps:
                        tasks.append(pool.submit(
                                  self.remove_fr,
                                  frp=frp.feature_relationship_id,
                                  ))
                if verbosity > 0:
                    self.stdout.write('Removing (using {} cpu)...'.format(cpu))
                    for task in tqdm(as_completed(tasks), total=len(tasks)):
                        if task.result():
                            raise(task.result())
                else:
                    for task in as_completed(tasks):
                        if task.result():
                            raise(task.result())
                if verbosity > 0:
                    self.stdout.write(self.style.SUCCESS('Done'))
                frps.delete()
                pool.shutdown()
            except IntegrityError as e:
                raise CommandError(
                        'It\'s not possible to delete every record. You must '
                        'delete relationships loaded after \'{}\' that might '
                        'depend on it. {}'.format(filename, e))
            except ObjectDoesNotExist:
                raise CommandError(
                        'Cannot remove \'{}\' (not registered)'.format(
                            filename))
        # *** if executing machado tests, do not use --cpu in call_command ***
        else:
            try:
                frps = FeatureRelationshipprop.objects.filter(
                        value=filename,
                        type_id=cvterm_contained_in.cvterm_id)
                if verbosity > 0:
                    self.stdout.write('Removing...')
                    for frp in tqdm(frps, total=len(frps)):
                        FeatureRelationship.objects.filter(
                            feature_relationship_id=frp.feature_relationship_id
                            ).delete()
                else:
                    for frp in frps:
                        FeatureRelationship.objects.filter(
                            feature_relationship_id=frp.feature_relationship_id
                            ).delete()
                frps.delete()
                if verbosity > 0:
                    self.stdout.write(self.style.SUCCESS('Done'))
            except IntegrityError as e:
                raise CommandError(
                        'It\'s not possible to delete every record. You must '
                        'delete relationships loaded after \'{}\' that might '
                        'depend on it. {}'.format(filename, e))
            except ObjectDoesNotExist:
                raise CommandError(
                        'Cannot remove \'{}\' (not registered)'.format(
                            filename))
