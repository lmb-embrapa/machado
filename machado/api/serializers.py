# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Serializers."""
from machado.loaders.common import retrieve_ontology_term
from machado.models import Analysis, Analysisfeature
from machado.models import Cv, Cvterm, Db, Dbxref
from machado.models import Feature, Featureloc, FeatureRelationship
from machado.models import Organism
from rest_framework import serializers


class AnalysisSerializer(serializers.ModelSerializer):
    """Analysis serializer."""

    match_count = serializers.SerializerMethodField()

    class Meta:
        """Meta."""

        model = Analysis
        fields = ('analysis_id', 'program', 'programversion', 'sourcename',
                  'timeexecuted', 'match_count', )

    def get_match_count(self, obj):
        """Get the number of matches."""
        return obj.Analysisfeature_analysis_Analysis.count()


class AnalysisfeatureSerializer(serializers.ModelSerializer):
    """Analysis feature serializer."""

    class Meta:
        """Meta."""

        model = Analysisfeature
        fields = ('rawscore', 'normscore', 'significance', 'identity')


class CvSerializer(serializers.HyperlinkedModelSerializer):
    """Cv serializer."""

    cvterm_count = serializers.SerializerMethodField()

    class Meta:
        """Meta."""

        model = Cv
        fields = ('cv_id', 'name', 'definition', 'cvterm_count')

    def get_cvterm_count(self, obj):
        """Get the number of child cvterms."""
        return obj.Cvterm_cv_Cv.count()


class CvtermSerializer(serializers.HyperlinkedModelSerializer):
    """Cvterm serializer."""

    class Meta:
        """Meta."""

        model = Cvterm
        depth = 1
        fields = ('cvterm_id', 'name', 'definition', 'dbxref', 'cv')


class DbSerializer(serializers.HyperlinkedModelSerializer):
    """Db serializer."""

    dbxref_count = serializers.SerializerMethodField()

    class Meta:
        """Meta."""

        model = Db
        fields = ('db_id', 'name', 'description', 'urlprefix', 'url',
                  'dbxref_count')

    def get_dbxref_count(self, obj):
        """Get the number of child dbxrefs."""
        return obj.Dbxref_db_Db.count()


class DbxrefSerializer(serializers.HyperlinkedModelSerializer):
    """Dbxref serializer."""

    class Meta:
        """Meta."""

        model = Dbxref
        depth = 1
        fields = ('dbxref_id', 'accession', 'description', 'version', 'db')


class FeatureLocSerializer(serializers.HyperlinkedModelSerializer):
    """FeatureLoc serializer."""

    class Meta:
        """Meta."""

        model = Featureloc
        fields = ('feature_id', 'srcfeature_id', 'fmin', 'fmax',
                  'strand', 'phase')


class FeatureSerializer(serializers.HyperlinkedModelSerializer):
    """Feature serializer."""

    Featureloc_feature_Feature = FeatureLocSerializer(many=True)
    match_count = serializers.SerializerMethodField()

    class Meta:
        """Meta."""

        model = Feature
        fields = ('feature_id', 'name', 'uniquename', 'md5checksum',
                  'organism', 'dbxref', 'match_count',
                  'Featureloc_feature_Feature')

    def get_match_count(self, obj):
        """Get the number of matches in featureloc."""
        return obj.Featureloc_srcfeature_Feature.count()


class OrganismSerializer(serializers.ModelSerializer):
    """Organism serializer."""

    class Meta:
        """Meta."""

        model = Organism
        fields = ('organism_id', 'abbreviation', 'genus', 'species',
                  'common_name', 'infraspecific_name')


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
        location = obj.Featureloc_feature_Feature.first()

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


class JBrowseTranscriptSerializer(serializers.ModelSerializer):
    """JBrowse transcript serializer."""

    start = serializers.SerializerMethodField()
    end = serializers.SerializerMethodField()
    strand = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    uniqueID = serializers.SerializerMethodField()
    subfeatures = serializers.SerializerMethodField()
    seq = serializers.SerializerMethodField()

    class Meta:
        """Meta."""

        model = Feature
        fields = ('uniqueID', 'name', 'type', 'start', 'end', 'strand',
                  'subfeatures', 'seq')

#        fields = ('start', 'end')

    def get_start(self, obj):
        """Get the start location."""
        try:
            feature_loc = obj.Featureloc_feature_Feature.first()
            return feature_loc.fmin
        except AttributeError:
            return 1

    def get_end(self, obj):
        """Get the end location."""
        try:
            feature_loc = obj.Featureloc_feature_Feature.first()
            return feature_loc.fmax
        except AttributeError:
            return obj.seqlen

    def get_strand(self, obj):
        """Get the strand."""
        try:
            feature_loc = obj.Featureloc_feature_Feature.first()
            return feature_loc.strand
        except AttributeError:
            pass

    def get_type(self, obj):
        """Get the type."""
        feat_type = Cvterm.objects.get(cvterm_id=obj.type_id).name
        return feat_type

    def get_uniqueID(self, obj):
        """Get the uniquename."""
        return obj.uniquename

    def get_subfeatures(self, obj):
        """Get the subfeatures."""
        part_of = retrieve_ontology_term(ontology='sequence', term='part_of')
        relationship = FeatureRelationship.objects.filter(
            subject_id=obj.feature_id,
            type_id=part_of.cvterm_id)
        result = list()
        for feat in relationship:
            feat_obj = Feature.objects.get(feature_id=feat.object_id)
            feat_dict = dict()
            feat_dict['type'] = Cvterm.objects.get(
                cvterm_id=feat_obj.type_id).name
            feature_loc = feat_obj.Featureloc_feature_Feature.first()
            feat_dict['start'] = feature_loc.fmin
            feat_dict['end'] = feature_loc.fmax
            feat_dict['strand'] = feature_loc.strand
            feat_dict['phase'] = feature_loc.phase
            result.append(feat_dict)
        return result

    def get_seq(self, obj):
        """Get the sequence."""
        return obj.residues
