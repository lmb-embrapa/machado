# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Serializers."""

from machado.models import Analysis, Analysisfeature
from machado.models import Cv, Cvterm, Db, Dbxref, Feature, Organism
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


class FeatureSerializer(serializers.HyperlinkedModelSerializer):
    """Feature serializer."""

    match_count = serializers.SerializerMethodField()

    class Meta:
        """Meta."""

        model = Feature
        fields = ('feature_id', 'name', 'uniquename', 'md5checksum',
                  'organism', 'dbxref', 'match_count')

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
