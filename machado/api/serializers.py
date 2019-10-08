# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Serializers."""
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from machado.models import Feature, Featureloc
from machado.models import FeatureRelationship


class JBrowseGlobalSerializer(serializers.Serializer):
    """JBrowse Global settings serializer."""

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
        return obj
