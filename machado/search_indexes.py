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
VALID_PROGRAMS = (
    Analysis.objects.filter(program__in=["interproscan", "diamond", "blast"])
    .distinct("program")
    .values_list("program")
)


class FeatureIndex(indexes.SearchIndex, indexes.Indexable):
    """Feature index."""

    text = indexes.CharField(document=True, null=True)
    autocomplete = indexes.EdgeNgramField(null=True)
    organism = indexes.CharField(faceted=True)
    so_term = indexes.CharField(model_attr="type__name", faceted=True)
    uniquename = indexes.CharField(model_attr="uniquename", faceted=True)
    name = indexes.CharField(model_attr="name", faceted=True, null=True)
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
    biomaterial = indexes.MultiValueField(faceted=True)
    treatment = indexes.MultiValueField(faceted=True)
    # orthologs_biomaterial = indexes.MultiValueField(faceted=True)
    orthologs_coexpression = indexes.MultiValueField(faceted=True)

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
        for i in list(VALID_PROGRAMS):
            if i in list(match_part_programs):
                result.append("{} matches".format(i[0]))
            else:
                result.append("no {} matches".format(i[0]))

        return result

    def prepare_text(self, obj):
        """Prepare text."""
        keywords = set()

        # Featureprop: display or product or description or note (in that order)
        if obj.get_display():
            keywords.add(obj.get_display())

        # GO terms
        feature_cvterm = FeatureCvterm.objects.filter(feature=obj)
        for i in feature_cvterm:
            term = "{}:{}".format(i.cvterm.dbxref.db.name, i.cvterm.dbxref.accession)
            keywords.add(term)
            keywords.add(i.cvterm.name)

        # Protein matches
        feature_relationships = FeatureRelationship.objects.filter(
            object=obj,
            subject__type__name="protein_match",
            subject__type__cv__name="sequence",
        )
        for feature_relationship in feature_relationships:
            keywords.add(feature_relationship.subject.uniquename)
            if feature_relationship.subject.name is not None:
                keywords.add(feature_relationship.subject.name)

        # Expression samples
        for sample in obj.get_expression_samples():
            keywords.add(sample.get("assay_name"))
            keywords.add(sample.get("biomaterial_name"))
            for i in sample.get("biomaterial_description").split(" "):
                keywords.add(i)
            for i in sample.get("treatment_name").split(" "):
                keywords.add(i)

        self.temp = " ".join(keywords)
        return " ".join(keywords)

    def prepare_orthology(self, obj):
        """Prepare orthology."""
        return bool(obj.get_orthologous_group())

    def prepare_orthologous_group(self, obj):
        """Prepare orthology."""
        return obj.get_orthologous_group()

    def prepare_coexpression(self, obj):
        """Prepare coexpression."""
        return bool(obj.get_coexpression_group())

    def prepare_coexpression_group(self, obj):
        """Prepare coepxression group."""
        return obj.get_coexpression_group()

    def prepare_biomaterial(self, obj):
        """Prepare biomaterial."""
        result = list()
        for sample in obj.get_expression_samples():
            if sample.get("biomaterial_description") not in result:
                result.append(sample.get("biomaterial_description"))
        return result

    def prepare_treatment(self, obj):
        """Prepare biomaterial."""
        result = list()
        for sample in obj.get_expression_samples():
            if sample.get("treatment_name") not in result:
                result.append(sample.get("treatment_name"))
        return result

    def prepare_orthologs_biomaterial(self, obj):
        """Prepare orthologs biomaterial."""
        result = list()
        try:
            ortholog_group = Featureprop.objects.get(
                type__cv__name="feature_property",
                type__name="orthologous group",
                feature=obj,
            ).value
        except ObjectDoesNotExist:
            return result

        protein_ids = Featureprop.objects.filter(
            type__cv__name="feature_property",
            type__name="orthologous group",
            value=ortholog_group,
        ).values_list("feature_id", flat=True)

        for mrna_protein_obj in FeatureRelationship.objects.filter(
            type__name="translation_of", object_id__in=protein_ids
        ):
            # mrna_protein_obj.subject == mRNA
            for sample in mrna_protein_obj.subject.get_expression_samples():
                if sample.get("biomaterial_description") not in result:
                    result.append(sample.get("biomaterial_description"))
        return result

    def prepare_orthologs_coexpression(self, obj):
        """Prepare orthologs coexpression."""
        try:
            ortholog_group = Featureprop.objects.get(
                type__cv__name="feature_property",
                type__name="orthologous group",
                feature=obj,
            ).value
        except ObjectDoesNotExist:
            return False

        protein_ids = Featureprop.objects.filter(
            type__cv__name="feature_property",
            type__name="orthologous group",
            value=ortholog_group,
        ).values_list("feature_id", flat=True)

        for mrna_protein_obj in FeatureRelationship.objects.filter(
            type__name="translation_of", object_id__in=protein_ids
        ):
            # mrna_protein_obj.subject == mRNA
            have_coexp = Featureprop.objects.filter(
                type__cv__name="feature_property",
                type__name="coexpression group",
                feature=mrna_protein_obj.subject,
            ).exists()
            if have_coexp:
                return True
        return False

    def prepare_autocomplete(self, obj):
        """Prepare autocomplete."""
        return '{} {} {}'.format(obj.organism.genus, obj.organism.species, self.temp)
