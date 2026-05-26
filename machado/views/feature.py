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

from machado.models import (
    Pub,
    Feature,
    Featureloc,
    FeatureCvterm,
    FeatureRelationship,
)
from django.db.models import F, Value
from django.db.models.functions import Concat


class FeatureView(View):
    """Feature views."""

    def retrieve_feature_data(
        self, feature_obj: Feature, load_list: list
    ) -> Dict[str, Any]:
        """Retrieve feature data."""
        result = dict()  # type: Dict[str, Any]

        # Functional annotation flags
        result["has_cvterm"] = FeatureCvterm.objects.filter(
            feature_id=feature_obj.feature_id
        ).exists()
        result["has_protein_matches"] = FeatureRelationship.objects.filter(
            object_id=feature_obj.feature_id,
            subject__type__name="protein_match",
            subject__type__cv__name="sequence",
        ).exists()

        if "functional" in load_list:
            result["cvterm_data"] = feature_obj.get_cvterm()
            result["protein_matches_data"] = FeatureRelationship.objects.filter(
                object_id=feature_obj.feature_id,
                subject__type__name="protein_match",
                subject__type__cv__name="sequence",
            ).values(
                db=F("subject__dbxref__db__name"),
                subject_uniquename=F("subject__uniquename"),
                subject_name=F("subject__name"),
            )

        # Similarity
        result["has_similarity"] = Featureloc.objects.filter(
            srcfeature_id=feature_obj.feature_id, feature__type__name__contains="match"
        ).exists()

        if "similarity" in load_list:
            result["similarity_data"] = []
            matches = (
                Featureloc.objects.filter(
                    srcfeature_id=feature_obj.feature_id,
                    feature__type__name__contains="match",
                )
                .select_related("feature")
                .prefetch_related(
                    "feature__Analysisfeature_feature_Feature",
                    "feature__Analysisfeature_feature_Feature__analysis",
                )
            )

            for m in matches:
                # Find the corresponding hit (the other featureloc for the same 'match' feature)
                hit_loc = (
                    Featureloc.objects.filter(feature_id=m.feature_id)
                    .exclude(srcfeature_id=feature_obj.feature_id)
                    .select_related(
                        "srcfeature", "srcfeature__dbxref__db", "srcfeature__type"
                    )
                    .first()
                )

                if not hit_loc:
                    continue

                # Get analysis data (stored on the 'match' feature)
                try:
                    analysis_feat = m.feature.Analysisfeature_feature_Feature.first()
                except AttributeError:
                    analysis_feat = None

                if not analysis_feat:
                    continue

                result["similarity_data"].append(
                    {
                        "program": analysis_feat.analysis.program,
                        "programversion": analysis_feat.analysis.programversion,
                        "db_name": (
                            hit_loc.srcfeature.dbxref.db.name
                            if hit_loc.srcfeature.dbxref
                            and hit_loc.srcfeature.dbxref.db
                            else "N/A"
                        ),
                        "uniquename": hit_loc.srcfeature.uniquename,
                        "name": hit_loc.srcfeature.name,
                        "query_start": m.fmin,
                        "query_end": m.fmax,
                        "score": (
                            analysis_feat.normscore
                            if analysis_feat.normscore is not None
                            else analysis_feat.rawscore
                        ),
                        "evalue": (
                            "{:.2e}".format(analysis_feat.significance)
                            if analysis_feat.significance is not None
                            else "N/A"
                        ),
                        "sotype": hit_loc.srcfeature.type.name,
                    }
                )

        # Expression
        result["has_expression"] = (
            feature_obj.type.name == "mRNA" and feature_obj.get_expression_samples()
        )
        if "expression" in load_list:
            result["expression_data"] = feature_obj.get_expression_samples()

        # Orthologs
        result["has_orthologs"] = bool(feature_obj.get_orthologous_group())
        if "orthologs" in load_list:
            ortholog_group = feature_obj.get_orthologous_group()
            result["ortholog_group"] = ortholog_group
            result["orthologs_data"] = Feature.objects.filter(
                type__name="polypeptide",
                Featureprop_feature_Feature__type__name="orthologous group",
                Featureprop_feature_Feature__value=ortholog_group,
            ).annotate(
                organism_name=Concat(
                    F("organism__genus"), Value(" "), F("organism__species")
                )
            )

        # Sequence
        result["has_sequence"] = bool(feature_obj.residues)
        if "sequence" in load_list:
            result["sequence_data"] = feature_obj.residues

        # Publications
        result["has_pubs"] = Pub.objects.filter(
            FeaturePub_pub_Pub__feature__feature_id=feature_obj.feature_id
        ).exists()
        if "pubs" in load_list:
            result["pubs_data"] = Pub.objects.filter(
                FeaturePub_pub_Pub__feature__feature_id=feature_obj.feature_id
            )

        return result

    def get(self, request):
        """Get queryset."""
        feature_id = request.GET.get("feature_id")
        if feature_id:
            feature_id = feature_id.replace(",", "")
        load_list = request.GET.getlist("load")

        try:
            feature_obj = Feature.objects.get(feature_id=feature_id)
        except ObjectDoesNotExist:
            error = {"error": "Feature not found."}
            return render(request, "error.html", {"context": error})

        user = getattr(request, "user", None)
        is_authenticated = user.is_authenticated if user else False
        if not is_authenticated and not feature_obj.organism.is_public:
            error = {"error": "Feature not found."}
            return render(request, "error.html", {"context": error}, status=404)

        data = self.retrieve_feature_data(feature_obj=feature_obj, load_list=load_list)

        return render(
            request,
            "feature.html",
            {"feature": feature_obj, "data": data, "load_list": load_list},
        )
