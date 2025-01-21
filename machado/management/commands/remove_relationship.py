# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Remove relationship."""

import os

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError

from machado.loaders.exceptions import ImportingError
from machado.models import Cvterm, FeatureRelationship, History


class Command(BaseCommand):
    """Remove relationship."""

    help = "Remove relationship"

    def add_arguments(self, parser):
        """Define the arguments."""
        parser.add_argument(
            "--file", help="name of the file (e.g.: groups.txt", required=True, type=str
        )

    def handle(self, file: str, verbosity: int = 0, **options):
        """Execute the main function."""
        history_obj = History()
        history_obj.start(command="remove_relationship", params=locals())
        # get cvterm for located in
        try:
            cvterm = Cvterm.objects.get(name="located in", cv__name="relationship")
        except IntegrityError as e:
            history_obj.failure(description=str(e))
            raise ImportingError(e)
        filename = os.path.basename(file)
        if verbosity > 0:
            self.stdout.write("Removing ...")
        try:
            FeatureRelationship.objects.filter(
                FeatureRelationshipprop_feature_relationship_FeatureRelationship__value=filename,
                FeatureRelationshipprop_feature_relationship_FeatureRelationship__type=cvterm,
            ).delete()

            history_obj.success(description="Done")
            if verbosity > 0:
                self.stdout.write(self.style.SUCCESS("Done"))
        except IntegrityError as e:
            history_obj.failure(
                description="It's not possible to delete every record. You must delete relationships loaded after '{}' that might depend on it. {}".format(
                    filename, e
                )
            )
            raise CommandError(
                "It's not possible to delete every record. You must "
                "delete relationships loaded after '{}' that might "
                "depend on it. {}".format(filename, e)
            )
        except ObjectDoesNotExist:
            raise CommandError("Cannot remove '{}' (not registered)".format(filename))
