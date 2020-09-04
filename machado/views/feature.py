# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""feature views."""

from typing import Any, Dict

from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.views import View

from machado.models import Pub
from machado.models import Feature, Featureloc
from machado.models import FeatureCvterm, FeatureRelationship

VALID_TYPES = ["gene", "mRNA", "polypeptide"]


class FeatureView(View):
    """Feature views."""

    def retrieve_feature_data(self, feature_obj: Feature) -> Dict[str, Any]:
        """Retrieve feature data."""
        result = dict()  # type: Dict[str, Any]

        result["cvterm"] = FeatureCvterm.objects.filter(
            feature_id=feature_obj.feature_id
        ).exists()
        result["protein_matches"] = FeatureRelationship.objects.filter(
            object_id=feature_obj.feature_id,
            subject__type__name="protein_match",
            subject__type__cv__name="sequence",
        ).exists()
        result["similarity"] = Featureloc.objects.filter(
            srcfeature_id=feature_obj.feature_id
        ).exists()
        result["pubs"] = Pub.objects.filter(
            FeaturePub_pub_Pub__feature__feature_id=feature_obj.feature_id
        ).exists()
        return result

    def get(self, request):
        """Get queryset."""
        feature_id = request.GET.get("feature_id")

        feature = dict()
        feature["feature_id"] = feature_id

        try:
            feature_obj = Feature.objects.get(feature_id=feature_id)
        except ObjectDoesNotExist:
            error = {"error": "Feature not found."}
            return render(request, "error.html", {"context": error})

        feature["type"] = feature_obj.type.name
        if feature["type"] not in VALID_TYPES:
            error = {"error": "Invalid feature type."}
            return render(request, "error.html", {"context": error})

        data = self.retrieve_feature_data(feature_obj=feature_obj)

        return render(request, "feature.html", {"feature": feature_obj, "data": data})
