# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Decorators."""
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Value, F, Q
from django.db.models.functions import Concat


VALID_TYPES = ["gene", "mRNA", "polypeptide"]


def get_feature_product(self):
    """Get the product feature prop."""
    try:
        return self.Featureprop_feature_Feature.get(
            type__name="product", type__cv__name="feature_property"
        ).value
    except ObjectDoesNotExist:
        return None


def get_feature_description(self):
    """Get the description feature prop."""
    try:
        return self.Featureprop_feature_Feature.get(
            type__name="description", type__cv__name="feature_property"
        ).value
    except ObjectDoesNotExist:
        return None


def get_feature_note(self):
    """Get the note feature prop."""
    try:
        return self.Featureprop_feature_Feature.get(
            type__name="note", type__cv__name="feature_property"
        ).value
    except ObjectDoesNotExist:
        return None


def get_feature_display(self):
    """Get the display feature prop."""
    try:
        return self.Featureprop_feature_Feature.get(
            type__name="display", type__cv__name="feature_property"
        ).value
    except ObjectDoesNotExist:
        if self.get_product() is not None:
            return self.get_product()
        elif self.get_description() is not None:
            return self.get_description()
        elif self.get_note() is not None:
            return self.get_note()
        else:
            return None


def get_feature_orthologous_group(self):
    """Get the orthologous group id."""
    try:
        return self.Featureprop_feature_Feature.get(
            type__cv__name="feature_property", type__name="orthologous group"
        ).value
    except ObjectDoesNotExist:
        return None


def get_feature_coexpression_group(self):
    """Get the coexpression group id."""
    try:
        return self.Featureprop_feature_Feature.get(
            type__cv__name="feature_property", type__name="coexpression group"
        ).value
    except ObjectDoesNotExist:
        return None


def get_feature_expression_samples(self):
    """Get the expression samples and treatments."""
    try:
        return list(
            self.Analysisfeature_feature_Feature.annotate(
                assay_name=F(
                    "analysis__Quantification_analysis_Analysis__acquisition__assay__name"
                )
            )
            .annotate(
                assay_description=F(
                    "analysis__Quantification_analysis_Analysis__acquisition__assay__description"
                )
            )
            .annotate(
                biomaterial_name=F(
                    "analysis__Quantification_analysis_Analysis__acquisition__assay__AssayBiomaterial_assay_Assay__biomaterial__name"
                )
            )
            .annotate(
                biomaterial_description=F(
                    "analysis__Quantification_analysis_Analysis__acquisition__assay__AssayBiomaterial_assay_Assay__biomaterial__description"
                )
            )
            .annotate(
                treatment_name=F(
                    "analysis__Quantification_analysis_Analysis__acquisition__assay__AssayBiomaterial_assay_Assay__biomaterial__Treatment_biomaterial_Biomaterial__name"
                )
            )
            .filter(normscore__gt=0)
            .exclude(assay_name__isnull=True)
            .values(
                "analysis__sourcename",
                "normscore",
                "assay_name",
                "assay_description",
                "biomaterial_name",
                "biomaterial_description",
                "treatment_name",
            )
        )
    except ObjectDoesNotExist:
        return None


def get_feature_relationship(self):
    """Get the relationships."""
    result = list()
    feature_relationships = self.FeatureRelationship_object_Feature.filter(
        Q(type__name="part_of") | Q(type__name="translation_of"),
        type__cv__name="sequence",
    )
    for feature_relationship in feature_relationships:
        if feature_relationship.subject.type.name in VALID_TYPES:
            result.append(feature_relationship.subject)
    feature_relationships = self.FeatureRelationship_subject_Feature.filter(
        Q(type__name="part_of") | Q(type__name="translation_of"),
        type__cv__name="sequence",
    )
    for feature_relationship in feature_relationships:
        if feature_relationship.object.type.name in VALID_TYPES:
            result.append(feature_relationship.object)

    if len(result) > 0:
        return result
    else:
        return None


def machadoFeatureMethods():
    """Add methods to machado.models.Feature."""

    def wrapper(cls):
        setattr(cls, "get_display", get_feature_display)
        setattr(cls, "get_product", get_feature_product)
        setattr(cls, "get_description", get_feature_description)
        setattr(cls, "get_note", get_feature_note)
        setattr(cls, "get_orthologous_group", get_feature_orthologous_group)
        setattr(cls, "get_coexpression_group", get_feature_coexpression_group)
        setattr(cls, "get_expression_samples", get_feature_expression_samples)
        setattr(cls, "get_relationship", get_feature_relationship)
        return cls

    return wrapper


def get_pub_authors(self):
    """Get a publication string."""
    return ", ".join(
        self.Pubauthor_pub_Pub.order_by("rank")
        .annotate(author=Concat("surname", Value(" "), "givennames"))
        .values_list("author", flat=True)
    )


def get_pub_doi(self):
    """Get a publication DOI."""
    return (
        self.PubDbxref_pub_Pub.filter(dbxref__db__name="DOI").first().dbxref.accession
    )


def machadoPubMethods():
    """Add methods to machado.models.Pub."""

    def wrapper(cls):
        setattr(cls, "get_authors", get_pub_authors)
        setattr(cls, "get_doi", get_pub_doi)
        return cls

    return wrapper
