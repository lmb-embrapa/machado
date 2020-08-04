# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Serializers."""
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from machado.models import Feature, Featureloc, Featureprop
from machado.models import FeatureRelationship
from machado.models import Pub


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
            "tracks": [],
            "objectName": obj.name,
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


class JBrowseVariantSerializer(serializers.ModelSerializer):
    """JBrowse variant serializer."""

    start = serializers.SerializerMethodField()
    end = serializers.SerializerMethodField()
    ref = serializers.SerializerMethodField()
    alt = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    qual = serializers.SerializerMethodField()

    class Meta:
        """Meta."""

        model = Feature
        fields = (
            "start",
            "end",
            "ref",
            "alt",
            "type",
            "id",
            "name",
            "qual",
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
            return 1

    def get_ref(self, obj):
        """Get the ref."""
        try:
            feature_loc = Featureloc.objects.get(
                feature_id=obj.feature_id, srcfeature_id=self.context.get("refseq")
            )
            ref = feature_loc.residue_info
            return ref
        except ObjectDoesNotExist:
            pass

    def get_alt(self, obj):
        """Get the alt."""
        try:
            feature_locs = Featureloc.objects.filter(
                feature_id=obj.feature_id, srcfeature_id=None
            )
            alt = ", ".join([obj.residue_info for obj in feature_locs])
            return alt
        except ObjectDoesNotExist:
            pass

    def get_type(self, obj):
        """Get the type."""
        feat_type = obj.type.name
        return feat_type

    def get_id(self, obj):
        """Get the id."""
        return obj.uniquename

    def get_name(self, obj):
        """Get the name."""
        return obj.name

    def get_qual(self, obj):
        """Get the qual."""
        try:
            featureprop = Featureprop.objects.get(
                feature_id=obj.feature_id,
                type__name="quality_value",
                type__cv__name="sequence",
            )
            return featureprop.value
        except ObjectDoesNotExist:
            return "."


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


class FeatureOrthologSerializer(serializers.ModelSerializer):
    """Feature sequence ortholog."""

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
