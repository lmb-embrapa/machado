"""Serializers."""

from chado.models import Cv, Cvterm, Organism
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

    class Meta:
        """Meta."""

        model = Cv
        fields = ('name', 'definition')


class CvtermSerializer(serializers.HyperlinkedModelSerializer):
    """Cvterm serializer."""

    class Meta:
        """Meta."""

        model = Cvterm
        fields = ('name', 'definition')
