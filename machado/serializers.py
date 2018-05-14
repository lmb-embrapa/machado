# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Serializers."""

from machado.models import Cv, Cvterm, Db, Dbxref, Feature, Organism
from rest_framework import serializers


class OrganismSerializer(serializers.ModelSerializer):
    """Organism serializer."""

    class Meta:
        """Meta."""

        model = Organism
        fields = ('organism_id', 'abbreviation', 'genus', 'species',
                  'common_name', 'infraspecific_name')


class CvSerializer(serializers.HyperlinkedModelSerializer):
    """Cv serializer."""

    count_cvterms = serializers.SerializerMethodField()

    class Meta:
        """Meta."""

        model = Cv
        fields = ('cv_id', 'name', 'definition', 'count_cvterms')

    def get_count_cvterms(self, obj):
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

    count_dbxrefs = serializers.SerializerMethodField()

    class Meta:
        """Meta."""

        model = Db
        fields = ('db_id', 'name', 'description', 'urlprefix', 'url',
                  'count_dbxrefs')

    def get_count_dbxrefs(self, obj):
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

    count_matches = serializers.SerializerMethodField()

    class Meta:
        """Meta."""

        model = Feature
        fields = ('feature_id', 'name', 'uniquename', 'md5checksum',
                  'organism', 'dbxref', 'count_matches')

    def get_count_matches(self, obj):
        """Get the number of matches in featureloc."""
        return obj.Featureloc_srcfeature_Feature.count()
