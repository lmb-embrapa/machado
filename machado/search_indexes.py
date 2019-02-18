# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Search indexes."""
from haystack import indexes
from django.db.models import Q
from machado.models import Feature, FeatureCvterm, Featureprop


VALID_TYPES = ['gene', 'mRNA', 'polypeptide']


class FeatureIndex(indexes.SearchIndex, indexes.Indexable):
    """Transcript index."""

    text = indexes.EdgeNgramField(document=True, null=True)
    organism = indexes.CharField(faceted=True)
    so_term = indexes.CharField(model_attr='type__name', faceted=True)
    uniquename = indexes.CharField(model_attr='uniquename', faceted=True)
    name = indexes.CharField(model_attr='name', faceted=True)

    def get_model(self):
        """Get model."""
        return Feature

    def index_queryset(self, using=None):
        """Index queryset."""
        return self.get_model().objects.filter(
            type__name__in=VALID_TYPES,
            type__cv__name='sequence',
            is_obsolete=False)

    def prepare_organism(self, obj):
        """Prepare organism."""
        return obj.organism.genus + ' ' + obj.organism.species

    def prepare_text(self, obj):
        """Prepare text."""
        keywords = list()
        keywords.append(obj.organism.genus + ' ' + obj.organism.species)

        display = Featureprop.objects.filter(
            ~Q(type__name='parent'),
            type__cv__name='feature_property',
            feature=obj)
        for i in display:
            keywords.append(i.value)

        feature_cvterm = FeatureCvterm.objects.filter(
            feature=obj)
        for i in feature_cvterm:
            keywords.append('{}:{}'.format(i.cvterm.dbxref.db.name,
                                           i.cvterm.dbxref.accession))
            keywords.append(i.cvterm.name)
        return '\n'.join(keywords)
