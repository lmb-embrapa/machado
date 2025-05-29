# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Serializers."""
from rest_framework import serializers


class FileSerializer(serializers.Serializer):
    """File serializer."""

    file = serializers.FileField()

class LoadPublicationSerializer(serializers.Serializer):
    file = serializers.FileField()
    cpu = serializers.IntegerField(required=False, min_value=1, default=1)

class OrganismSerializer(serializers.Serializer):
    """Organism serializer."""

    genus = serializers.CharField(required=True, help_text="The genus of the organism.")
    species = serializers.CharField(
        required=True, help_text="The species of the organism."
    )
    abbreviation = serializers.CharField(
        required=False, help_text="Abbreviation of the organism name."
    )
    common_name = serializers.CharField(
        required=False, help_text="Common name of the organism."
    )
    infraspecific_name = serializers.CharField(
        required=False, help_text="Infraspecific name of the organism."
    )
    comment = serializers.CharField(
        required=False, help_text="Additional comments about the organism."
    )
