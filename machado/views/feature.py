# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""feature views."""

from typing import Any, Dict, List

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.views import View

from machado.models import Analysis, Analysisfeature, Pub
from machado.models import Feature, Featureloc, Featureprop
from machado.models import FeatureCvterm, FeatureDbxref, FeatureRelationship

VALID_TYPES = ["gene", "mRNA", "polypeptide"]


class FeatureView(View):
    """Feature views."""

    def retrieve_feature_location(self, feature_id: int, organism: str) -> List[Dict]:
        """Retrieve feature locations."""
        result = list()
        for location in Featureloc.objects.filter(feature_id=feature_id):
            jbrowse_url = None
            if hasattr(settings, "MACHADO_JBROWSE_URL"):
                if hasattr(settings, "MACHADO_JBROWSE_OFFSET"):
                    offset = settings.MACHADO_JBROWSE_OFFSET
                else:
                    offset = 1000
                loc = "{}:{}..{}".format(
                    Feature.objects.get(feature_id=location.srcfeature_id).uniquename,
                    location.fmin - offset,
                    location.fmax + offset,
                )
                jbrowse_url = (
                    "{}/?data=data/{}&loc={}"
                    "&tracklist=0&nav=0&overview=0"
                    "&tracks=ref_seq,gene,transcripts,CDS".format(
                        settings.MACHADO_JBROWSE_URL, organism, loc
                    )
                )
            result.append(
                {
                    "start": location.fmin,
                    "end": location.fmax,
                    "strand": location.strand,
                    "ref": Feature.objects.get(
                        feature_id=location.srcfeature_id
                    ).uniquename,
                    "jbrowse_url": jbrowse_url,
                }
            )
        return result

    def retrieve_feature_dbxref(self, feature_id: int) -> List[Dict]:
        """Retrieve feature dbxrefs."""
        feature_dbxref = FeatureDbxref.objects.filter(feature_id=feature_id)
        result = list()
        for feature_dbxref in feature_dbxref:
            result.append(
                {
                    "dbxref": feature_dbxref.dbxref.accession,
                    "db": feature_dbxref.dbxref.db.name,
                }
            )
        return result

    def retrieve_feature_cvterm(self, feature_id: int) -> List[Dict]:
        """Retrieve feature cvterms."""
        feature_cvterm = FeatureCvterm.objects.filter(feature_id=feature_id)
        result = list()
        for feature_cvterm in feature_cvterm:
            result.append(
                {
                    "cvterm": feature_cvterm.cvterm.name,
                    "cvterm_definition": feature_cvterm.cvterm.definition,
                    "cv": feature_cvterm.cvterm.cv.name,
                    "db": feature_cvterm.cvterm.dbxref.db.name,
                    "dbxref": feature_cvterm.cvterm.dbxref.accession,
                }
            )
        return result

    def retrieve_feature_protein_matches(self, feature_id: int) -> List[Dict]:
        """Retrieve feature relationships."""
        feature_relationships = FeatureRelationship.objects.filter(
            object_id=feature_id,
            subject__type__name="protein_match",
            subject__type__cv__name="sequence",
        )
        result = list()
        for feature_relationship in feature_relationships:
            result.append(
                {
                    "subject_id": feature_relationship.subject.uniquename,
                    "subject_desc": feature_relationship.subject.name,
                    "db": feature_relationship.subject.dbxref.db.name,
                    "dbxref": feature_relationship.subject.dbxref.accession,
                }
            )
        return result

    def retrieve_feature_similarity(self, feature_id: int, organism_id: int) -> List:
        """Retrieve feature locations."""
        result = list()
        try:
            match_parts_ids = (
                Featureloc.objects.filter(srcfeature_id=feature_id)
                .filter(feature__organism_id=organism_id)
                .values_list("feature_id")
            )
        except ObjectDoesNotExist:
            return list()

        for match_part_id in match_parts_ids:
            analysis_feature = Analysisfeature.objects.get(feature_id=match_part_id)
            analysis = Analysis.objects.get(analysis_id=analysis_feature.analysis_id)
            if analysis_feature.normscore is not None:
                score = analysis_feature.normscore
            else:
                score = analysis_feature.rawscore

            # it should have 2 records (query and hit)
            matches = Featureloc.objects.filter(feature_id=match_part_id)
            for match in matches:
                # query
                if match.srcfeature_id == feature_id:
                    query_start = match.fmin
                    query_end = match.fmax
                # hit
                else:
                    match_feat = Feature.objects.get(feature_id=match.srcfeature_id)

                    if match_feat.dbxref.db.name == "GFF_SOURCE":
                        db_name = None
                    else:
                        db_name = match_feat.dbxref.db.name

                    feature_cvterm = self.retrieve_feature_cvterm(
                        feature_id=match_feat.feature_id
                    )

            feature_cvterm = self.retrieve_feature_cvterm(
                feature_id=match_feat.feature_id
            )

            result.append(
                {
                    "program": analysis.program,
                    "programversion": analysis.programversion,
                    "db_name": db_name,
                    "unique": match_feat.uniquename,
                    "name": match_feat.name,
                    "display": match_feat.get_display,
                    "query_start": query_start,
                    "query_end": query_end,
                    "score": score,
                    "evalue": analysis_feature.significance,
                    "feature_cvterm": feature_cvterm,
                }
            )

        return result

    def retrieve_feature_orthologs(self, feature_id: int) -> Dict[str, Any]:
        """Retrieve feature orthologs."""
        result: Dict[str, List] = dict()
        try:
            orthologous_group = Featureprop.objects.get(
                type__name="orthologous group",
                type__cv__name="feature_property",
                feature_id=feature_id,
            ).value
            for feature in Feature.objects.filter(
                Featureprop_feature_Feature__value=orthologous_group
            ).only("feature_id", "uniquename", "type"):
                if feature.type.name in VALID_TYPES:
                    result.setdefault(orthologous_group, []).append(feature)
        except ObjectDoesNotExist:
            pass

        return result

    def retrieve_feature_pub(self, feature_id: int) -> List[Pub]:
        """Retrieve feature publications."""
        return Pub.objects.filter(FeaturePub_pub_Pub__feature__feature_id=feature_id)

    def retrieve_feature_data(self, feature_obj: Feature) -> Dict[str, Any]:
        """Retrieve feature data."""
        result = dict()  # type: Dict[str, Any]

        result["location"] = self.retrieve_feature_location(
            feature_id=feature_obj.feature_id,
            organism="{} {}".format(
                feature_obj.organism.genus, feature_obj.organism.species
            ),
        )
        result["dbxref"] = self.retrieve_feature_dbxref(
            feature_id=feature_obj.feature_id
        )
        result["cvterm"] = self.retrieve_feature_cvterm(
            feature_id=feature_obj.feature_id
        )
        result["protein_matches"] = self.retrieve_feature_protein_matches(
            feature_id=feature_obj.feature_id
        )
        result["similarity"] = self.retrieve_feature_similarity(
            feature_id=feature_obj.feature_id, organism_id=feature_obj.organism_id
        )
        result["orthologs"] = self.retrieve_feature_orthologs(
            feature_id=feature_obj.feature_id
        )
        result["pubs"] = self.retrieve_feature_pub(feature_id=feature_obj.feature_id)
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
