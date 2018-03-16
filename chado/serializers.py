"""Serializers."""

from chado.models import Organism
from rest_framework import serializers


class OrganismSerializer(serializers.HyperlinkedModelSerializer):
    """Organism serializer."""

    class Meta:
        """Meta."""

        model = Organism
        fields = ('organism_id', 'abbreviation', 'genus', 'species',
                  'common_name', 'infraspecific_name')
