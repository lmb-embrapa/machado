"""Search indexes."""
from haystack import indexes
from django.db.models import Q
from machado.models import Feature, FeatureCvterm, Featureprop


class FeatureIndex(indexes.SearchIndex, indexes.Indexable):
    """Transcript index."""

    text = indexes.CharField(document=True, null=True)
    organism = indexes.CharField(faceted=True)
    so_term = indexes.CharField(model_attr='type__name', faceted=True)

    def get_model(self):
        """Get model."""
        return Feature

    def index_queryset(self, using=None):
        """Index queryset."""
        return self.get_model().objects.filter(
            Q(type__name='mRNA') | Q(type__name='polypeptide'),
            type__cv__name='sequence',
            is_obsolete=False)

    def prepare_organism(self, obj):
        """Prepare organism."""
        return obj.organism.genus + ' ' + obj.organism.species

    def prepare_text(self, obj):
        """Prepare text."""
        keywords = list()
        keywords.append(obj.uniquename)
        keywords.append(obj.name)

        display = Featureprop.objects.filter(
            type__cv__name='feature_property',
            type__name='display',
            feature=obj)
        for i in display:
            keywords += i.value.split()

        feature_cvterm = FeatureCvterm.objects.filter(
            feature=obj)
        for i in feature_cvterm:
            keywords.append('{}:{}'.format(i.cvterm.dbxref.db.name,
                                           i.cvterm.dbxref.accession))
            keywords += i.cvterm.name.split()

        return '\n'.join(keywords)
