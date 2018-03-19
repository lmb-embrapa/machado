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
        fields = ('cvterm_id', 'name', 'definition')
