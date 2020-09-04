# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Serializers."""
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from machado.models import Cvterm, Feature, Featureloc
from machado.models import FeatureRelationship
from machado.models import Pub


class JBrowseGlobalSerializer(serializers.Serializer):
    """JBrowse global settings serializer."""

    featureDensity = serializers.FloatField()


class JBrowseNamesSerializer(serializers.ModelSerializer):
    """JBrowse transcript serializer."""

    location = serializers.SerializerMethodField()

    class Meta:
        """Meta."""

        model = Feature
        fields = ("name", "location")

    def get_location(self, obj):
        """Get the location."""
        try:
            location = Featureloc.objects.get(feature_id=obj.feature_id)
        except ObjectDoesNotExist:
            return None

        ref = (
            Feature.objects.filter(feature_id=location.srcfeature_id)
            .values_list("uniquename", flat=True)
            .first()
        )

        return {
            "ref": ref,
            "start": location.fmin,
            "end": location.fmax,
            "type": obj.type.name,
            "tracks": [],
            "objectName": obj.uniquename,
        }


class JBrowseFeatureSerializer(serializers.ModelSerializer):
    """JBrowse transcript serializer."""

    start = serializers.SerializerMethodField()
    end = serializers.SerializerMethodField()
    strand = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    uniqueID = serializers.SerializerMethodField()
    subfeatures = serializers.SerializerMethodField()
    seq = serializers.SerializerMethodField()
    display = serializers.SerializerMethodField()

    class Meta:
        """Meta."""

        model = Feature
        fields = (
            "uniqueID",
            "name",
            "type",
            "start",
            "end",
            "strand",
            "subfeatures",
            "seq",
            "display",
        )

    def _get_location(self, obj):
        """Get the location."""
        try:
            feature_loc = Featureloc.objects.get(
                feature_id=obj.feature_id, srcfeature_id=self.context.get("refseq")
            )
            return feature_loc
        except ObjectDoesNotExist:
            pass

    def _get_subfeature(self, feature_id):
        """Get subfeature."""
        feature_loc = Featureloc.objects.get(
            feature_id=feature_id, srcfeature_id=self.context["refseq"]
        )
        return {
            "type": Feature.objects.filter(feature_id=feature_id)
            .values_list("type__name", flat=True)
            .first(),
            "start": feature_loc.fmin,
            "end": feature_loc.fmax,
            "strand": feature_loc.strand,
            "phase": feature_loc.phase,
        }

    def get_start(self, obj):
        """Get the start location."""
        if self.context.get("soType"):
            return self._get_location(obj).fmin
        else:
            return 1

    def get_end(self, obj):
        """Get the end location."""
        if self.context.get("soType"):
            return self._get_location(obj).fmax
        else:
            return obj.seqlen

    def get_strand(self, obj):
        """Get the strand."""
        try:
            return self._get_location(obj).strand
        except AttributeError:
            return None

    def get_type(self, obj):
        """Get the type."""
        feat_type = obj.type.name
        return feat_type

    def get_uniqueID(self, obj):
        """Get the uniquename."""
        return obj.uniquename

    def get_subfeatures(self, obj):
        """Get the subfeatures."""
        relationship = FeatureRelationship.objects.filter(
            subject_id=obj.feature_id, type__name="part_of", type__cv__name="sequence"
        )
        result = list()
        for feat in relationship:
            result.append(self._get_subfeature(feat.object_id))
        return result

    def get_seq(self, obj):
        """Get the sequence."""
        return obj.residues

    def get_display(self, obj):
        """Get the display."""
        return obj.get_display()


class JBrowseRefseqSerializer(serializers.ModelSerializer):
    """JBrowse transcript serializer."""

    start = serializers.SerializerMethodField()
    end = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()

    class Meta:
        """Meta."""

        model = Feature
        fields = ("name", "start", "end")

    def get_start(self, obj):
        """Get the start location."""
        return 1

    def get_end(self, obj):
        """Get the end location."""
        return obj.seqlen

    def get_name(self, obj):
        """Get the name."""
        return obj.uniquename


class autocompleteSerializer(serializers.Serializer):
    """autocomplete search serializer."""

    autocomplete = serializers.CharField()

    def to_representation(self, obj):
        """To representation."""
        return obj


class FeatureIDSerializer(serializers.Serializer):
    """Feature ID serializer."""

    feature_id = serializers.IntegerField()


class FeatureOrthologSerializer(serializers.ModelSerializer):
    """Feature ortholog group."""

    display = serializers.SerializerMethodField()
    organism = serializers.SerializerMethodField()

    class Meta:
        """Meta."""

        model = Feature
        fields = ("feature_id", "uniquename", "display", "organism")

    def get_display(self, obj):
        """Get the display."""
        return obj.get_display()

    def get_organism(self, obj):
        """Get the organism."""
        return "{} {}".format(obj.organism.genus, obj.organism.species)


class FeatureSequenceSerializer(serializers.ModelSerializer):
    """Feature sequence serializer."""

    sequence = serializers.SerializerMethodField()

    class Meta:
        """Meta."""

        model = Feature
        fields = ("sequence",)

    def get_sequence(self, obj):
        """Get the sequence."""
        return obj.residues


class FeaturePublicationSerializer(serializers.ModelSerializer):
    """Feature publication serializer."""

    authors = serializers.SerializerMethodField()
    doi = serializers.SerializerMethodField()

    class Meta:
        """Meta."""

        model = Pub
        fields = ("doi", "authors", "title", "series_name", "pyear", "volume", "pages")

    def get_authors(self, obj):
        """Get the authors."""
        return obj.get_authors()

    def get_doi(self, obj):
        """Get the doi."""
        return obj.get_doi()


class FeatureOntologySerializer(serializers.ModelSerializer):
    """Feature ontology term serializer."""

    cvterm = serializers.SerializerMethodField()
    cvterm_definition = serializers.SerializerMethodField()
    cv = serializers.SerializerMethodField()
    db = serializers.SerializerMethodField()
    dbxref = serializers.SerializerMethodField()

    class Meta:
        """Meta."""

        fields = ("cvterm", "cvterm_definition", "cv", "db", "dbxref")
        model = Cvterm

    def get_cvterm(self, obj):
        """Get the cvterm."""
        return obj.name

    def get_cvterm_definition(self, obj):
        """Get the cvterm definition."""
        return obj.definition

    def get_cv(self, obj):
        """Get the cv."""
        return obj.cv.name

    def get_db(self, obj):
        """Get the db."""
        return obj.dbxref.db.name

    def get_dbxref(self, obj):
        """Get the dbxref."""
        return obj.dbxref.accession


class FeatureProteinMatchesSerializer(serializers.ModelSerializer):
    """Feature protein matches serializer."""

    subject_id = serializers.SerializerMethodField()
    subject_desc = serializers.SerializerMethodField()
    db = serializers.SerializerMethodField()
    dbxref = serializers.SerializerMethodField()

    class Meta:
        """Meta."""

        fields = ("subject_id", "subject_desc", "db", "dbxref")
        model = Cvterm

    def get_subject_id(self, obj):
        """Get the subject id."""
        return obj.subject.uniquename

    def get_subject_desc(self, obj):
        """Get the subject name."""
        return obj.subject.name

    def get_db(self, obj):
        """Get the db."""
        return obj.subject.dbxref.db.name

    def get_dbxref(self, obj):
        """Get the dbxref."""
        return obj.subject.dbxref.accession


class FeatureSimilaritySerializer(serializers.Serializer):
    """Feature similarity matches serializer."""

    program = serializers.CharField()
    programversion = serializers.CharField()
    db_name = serializers.CharField()
    unique = serializers.CharField()
    name = serializers.CharField()
    sotype = serializers.CharField()
    query_start = serializers.CharField()
    query_end = serializers.CharField()
    score = serializers.CharField()
    evalue = serializers.CharField()


class FeatureCoexpressionSerializer(serializers.ModelSerializer):
    """Feature coexpression group."""

    display = serializers.SerializerMethodField()
    organism = serializers.SerializerMethodField()

    class Meta:
        """Meta."""

        model = Feature
        fields = ("feature_id", "uniquename", "display", "organism")

    def get_display(self, obj):
        """Get the display."""
        return obj.get_display()

    def get_organism(self, obj):
        """Get the organism."""
        return "{} {}".format(obj.organism.genus, obj.organism.species)


class FeatureExpressionSerializer(serializers.Serializer):
    """Feature similarity matches serializer."""

    analysis__sourcename = serializers.CharField()
    normscore = serializers.FloatField()
    assay_name = serializers.CharField()
    assay_description = serializers.CharField()
    biomaterial_name = serializers.CharField()
    biomaterial_description = serializers.CharField()
    treatment_name = serializers.CharField()


class FeatureInfoSerializer(serializers.ModelSerializer):
    """Feature info serializer."""

    display = serializers.SerializerMethodField()
    product = serializers.SerializerMethodField()
    note = serializers.SerializerMethodField()
    organism = serializers.SerializerMethodField()
    relationship = serializers.SerializerMethodField()
    dbxref = serializers.SerializerMethodField()

    class Meta:
        """Meta."""

        model = Feature
        fields = (
            "uniquename",
            "display",
            "product",
            "note",
            "organism",
            "relationship",
            "dbxref",
        )

    def get_display(self, obj):
        """Get the display."""
        return obj.get_display()

    def get_organism(self, obj):
        """Get the organism."""
        return "{} {}".format(obj.organism.genus, obj.organism.species)

    def get_relationship(self, obj):
        """Get the relationship."""
        result = list()
        try:
            for relative in obj.get_relationship():
                result.append(
                    {
                        "relative_feature_id": relative.feature_id,
                        "relative_type": relative.type.name,
                        "relative_uniquename": relative.uniquename,
                        "relative_display": relative.get_display(),
                    }
                )
        except TypeError:
            pass
        return result

    def get_dbxref(self, obj):
        """Get the dbxrefs."""
        return obj.get_dbxrefs()

    def get_product(self, obj):
        """Get the product."""
        return obj.get_product()

    def get_note(self, obj):
        """Get the note."""
        return obj.get_note()


class FeatureLocationSerializer(serializers.Serializer):
    """Feature location serializer."""

    start = serializers.IntegerField()
    end = serializers.IntegerField()
    strand = serializers.IntegerField()
    ref = serializers.CharField()
    jbrowse_url = serializers.CharField()
