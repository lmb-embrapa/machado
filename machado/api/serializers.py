# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Serializers."""
from django.core.exceptions import ObjectDoesNotExist
from machado.models import Cvterm, Feature, Featureloc
from machado.models import FeatureRelationship
from rest_framework import serializers


class JBrowseGlobalSerializer(serializers.Serializer):
    """JBrowse Global settings serializer."""

    featureDensity = serializers.FloatField()


class JBrowseNamesSerializer(serializers.ModelSerializer):
    """JBrowse transcript serializer."""

    location = serializers.SerializerMethodField()

    class Meta:
        """Meta."""

        model = Feature
        fields = ('name', 'location')

    def get_location(self, obj):
        """Get the location."""
        try:
            location = Featureloc.objects.get(feature_id=obj.feature_id)
        except ObjectDoesNotExist:
            location = None

        result = dict()

        if location is not None:
            ref = Feature.objects.get(
                feature_id=location.srcfeature_id).uniquename

            result = {
                'ref': ref,
                'start': location.fmin,
                'end': location.fmax,
                'tracks': [],
                'objectName': obj.name
            }

        return result


class JBrowseFeatureSerializer(serializers.ModelSerializer):
    """JBrowse transcript serializer."""

    _locs = dict()
    _subfeatures = dict()
    _types = dict()

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
        fields = ('uniqueID', 'name', 'type', 'start', 'end', 'strand',
                  'subfeatures', 'seq', 'display')

    def _get_location(self, obj):
        """Get the location."""
        if obj.feature_id not in self._locs:
            try:
                feature_loc = Featureloc.objects.get(
                    feature_id=obj.feature_id,
                    srcfeature_id=self.context.get('refseq'))
                self._locs = {obj.feature_id: feature_loc}
            except ObjectDoesNotExist:
                pass
        return self._locs.get(obj.feature_id)

    def _get_subfeature(self, feature_id):
        """Get subfeature."""
        if feature_id not in self._subfeatures:
            feat_obj = Feature.objects.get(feature_id=feature_id)
            # feature_loc = feat_obj.Featureloc_feature_Feature.first()
            feature_loc = Featureloc.objects.get(
                feature_id=feature_id, srcfeature_id=self.context['refseq'])
            self._subfeatures[feature_id] = {
                'type': Cvterm.objects.get(cvterm_id=feat_obj.type_id).name,
                'start': feature_loc.fmin,
                'end': feature_loc.fmax,
                'strand': feature_loc.strand,
                'phase': feature_loc.phase
            }
        return self._subfeatures.get(feature_id)

    def _get_type(self, cvterm_id):
        """Get cvterm from type_id."""
        if cvterm_id not in self._types:
            self._types = {
                cvterm_id: Cvterm.objects.get(cvterm_id=cvterm_id)
            }
        return self._types.get(cvterm_id)

    def get_start(self, obj):
        """Get the start location."""
        if self.context.get('soType'):
            return self._get_location(obj).fmin
        else:
            return 1

    def get_end(self, obj):
        """Get the end location."""
        if self.context.get('soType'):
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
        feat_type = self._get_type(obj.type_id).name
        return feat_type

    def get_uniqueID(self, obj):
        """Get the uniquename."""
        return obj.uniquename

    def get_subfeatures(self, obj):
        """Get the subfeatures."""
        relationship = FeatureRelationship.objects.filter(
            subject_id=obj.feature_id,
            type__name='part_of', type__cv__name='sequence')
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
        fields = ('name', 'start', 'end')

    def get_start(self, obj):
        """Get the start location."""
        return 1

    def get_end(self, obj):
        """Get the end location."""
        return obj.seqlen

    def get_name(self, obj):
        """Get the name."""
        return obj.uniquename
