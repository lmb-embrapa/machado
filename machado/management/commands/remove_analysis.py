# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Remove analysis."""

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError
from tqdm import tqdm

from machado.models import Analysisprop, Analysis, Analysisfeature
from machado.models import Cvterm, Feature, Featureloc
from machado.models import FeatureCvterm, FeatureCvtermprop
from machado.models import FeatureRelationship, FeatureRelationshipprop
from machado.models import Quantification, Acquisition


class Command(BaseCommand):
    """Remove analysis."""

    help = "Remove analysis (CASCADE). Also remove related features that are"
    "multispecies (features that were loaded from the analysis file only)."

    def add_arguments(self, parser):
        """Define the arguments."""
        parser.add_argument(
            "--name",
            help="source filename (analysisprop.value)",
            required=True,
            type=str,
        )

    def handle(self, name: str, verbosity: int = 1, **options):
        """Execute the main function."""
        if verbosity > 0:
            self.stdout.write(
                "Deleting {} and every child" "record (CASCADE)".format(name)
            )

        try:
            cvterm_contained_in = Cvterm.objects.get(
                name="contained in", cv__name="relationship"
            )
            analysisprop_list = Analysisprop.objects.filter(
                value=name, type_id=cvterm_contained_in.cvterm_id
            )

            for analysisprop in tqdm(
                analysisprop_list,
                total=len(analysisprop_list),
                disable=False if verbosity > 0 else True,
            ):
                analysis = Analysis.objects.get(analysis_id=analysisprop.analysis_id)
                # remove quantification and aquisition if exists...
                try:
                    quantification = Quantification.objects.get(analysis=analysis)
                    Acquisition.objects.filter(
                        acquisition_id=quantification.acquisition_id
                    ).delete()
                    quantification.delete()
                except ObjectDoesNotExist:
                    pass
                # remove analysisfeatures and others if exists...
                try:
                    cr_ids = list(
                        FeatureCvtermprop.objects.filter(
                            type=cvterm_contained_in, value=analysis.sourcename
                        ).values_list("feature_cvterm_id", flat=True)
                    )
                    FeatureCvterm.objects.filter(feature_cvterm_id__in=cr_ids).delete()

                    fr_ids = list(
                        FeatureRelationshipprop.objects.filter(
                            type=cvterm_contained_in, value=analysis.sourcename
                        ).values_list("feature_relationship_id", flat=True)
                    )
                    FeatureRelationship.objects.filter(
                        feature_relationship_id__in=fr_ids
                    ).delete()

                    feature_ids = list(
                        Analysisfeature.objects.filter(analysis=analysis).values_list(
                            "feature_id", flat=True
                        )
                    )
                    Featureloc.objects.filter(feature_id__in=feature_ids).delete()
                    # remove only features created by load_similarity
                    # type == match_part
                    Feature.objects.filter(
                        feature_id__in=feature_ids, type__name="match_part"
                    ).delete()
                    Analysisfeature.objects.filter(analysis=analysis).delete()
                except ObjectDoesNotExist:
                    pass
                # finally removes analysis...
                analysis.delete()
            if verbosity > 0:
                self.stdout.write(self.style.SUCCESS("Done"))
        except ObjectDoesNotExist:
            raise CommandError("Cannot remove {} (not registered)".format(name))
