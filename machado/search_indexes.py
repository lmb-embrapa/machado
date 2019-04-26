# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Search indexes."""
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from haystack import indexes

from machado.models import Analysis, Analysisfeature
from machado.models import Feature, FeatureCvterm, Featureprop
from machado.models import Featureloc, FeatureRelationship

VALID_TYPES = ["gene", "mRNA", "polypeptide"]
VALID_PROGRAMS = ["interproscan", "diamond", "blast"]


class FeatureIndex(indexes.SearchIndex, indexes.Indexable):
    """Transcript index."""

    text = indexes.CharField(document=True, null=True)
    autocomplete = indexes.EdgeNgramField(null=True)
    organism = indexes.CharField(faceted=True)
    so_term = indexes.CharField(model_attr="type__name", faceted=True)
    uniquename = indexes.CharField(model_attr="uniquename", faceted=True)
    name = indexes.CharField(model_attr="name", faceted=True)
    analyses = indexes.MultiValueField(faceted=True)
    if Featureprop.objects.filter(
        type__name="orthologous group", type__cv__name="feature_property"
    ).exists():
        orthology = indexes.BooleanField(faceted=True)
        orthologous_group = indexes.CharField(faceted=True)
    if Featureprop.objects.filter(
        type__name="coexpression group", type__cv__name="feature_property"
    ).exists():
        coexpression = indexes.BooleanField(faceted=True)
        coexpression_group = indexes.CharField(faceted=True)

    def get_model(self):
        """Get model."""
        return Feature

    def index_queryset(self, using=None):
        """Index queryset."""
        return self.get_model().objects.filter(
            type__name__in=VALID_TYPES, type__cv__name="sequence", is_obsolete=False
        )

    def prepare_organism(self, obj):
        """Prepare organism."""
        return obj.organism.genus + " " + obj.organism.species

    def prepare_analyses(self, obj):
        """Prepare analyses."""
        # similarity analyses
        programs = (
            Analysis.objects.filter(program__in=VALID_PROGRAMS)
            .distinct("program")
            .values_list("program")
        )
        match_part_ids = (
            Featureloc.objects.filter(srcfeature=obj)
            .filter(feature__organism_id=obj.organism_id)
            .filter(feature__type__name="match_part")
            .filter(feature__type__cv__name="sequence")
            .values_list("feature_id")
        )
        match_part_programs = (
            Analysisfeature.objects.filter(feature_id__in=match_part_ids)
            .values_list("analysis__program")
            .distinct()
        )
        result = list()
        for i in list(programs):
            if i in match_part_programs:
                result.append("{} matches".format(i[0]))
            else:
                result.append("no {} matches".format(i[0]))

        return result

    def prepare_text(self, obj):
        """Prepare text."""
        keywords = list()

        # Featureprop: display, description, note
        display = Featureprop.objects.filter(
            ~Q(type__name="parent"), type__cv__name="feature_property", feature=obj
        )
        for i in display:
            keywords.append(i.value)

        # GO terms
        feature_cvterm = FeatureCvterm.objects.filter(feature=obj)
        for i in feature_cvterm:
            keywords.append(
                "{}:{}".format(i.cvterm.dbxref.db.name, i.cvterm.dbxref.accession)
            )
            keywords.append(i.cvterm.name)

        # Protein matches
        feature_relationships = FeatureRelationship.objects.filter(
            object=obj,
            subject__type__name="protein_match",
            subject__type__cv__name="sequence",
        )
        for feature_relationship in feature_relationships:
            keywords.append(feature_relationship.subject.uniquename)
            if feature_relationship.subject.name is not None:
                keywords.append(feature_relationship.subject.name)

        self.temp = " ".join(keywords)
        return " ".join(keywords)

    def prepare_orthology(self, obj):
        """Prepare orthology."""
        return Featureprop.objects.filter(
            type__cv__name="feature_property",
            type__name="orthologous group",
            feature=obj,
        ).exists()

    def prepare_orthologous_group(self, obj):
        """Prepare orthology."""
        try:
            return Featureprop.objects.get(
                type__cv__name="feature_property",
                type__name="orthologous group",
                feature=obj,
            ).value
        except ObjectDoesNotExist:
            return None

    def prepare_coexpression(self, obj):
        """Prepare coexpression."""
        return Featureprop.objects.filter(
            type__cv__name="feature_property",
            type__name="coexpression group",
            feature=obj,
        ).exists()

    def prepare_coexpression_group(self, obj):
        """Prepare coepxression group."""
        try:
            return Featureprop.objects.get(
                type__cv__name="feature_property",
                type__name="coexpression group",
                feature=obj,
            ).value
        except ObjectDoesNotExist:
            return None

    def prepare_autocomplete(self, obj):
        """Prepare autocomplete."""
        return self.temp
