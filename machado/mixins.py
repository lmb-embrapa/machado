# Copyright 2026 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Model method mixins for Feature, Pub and Organism.

These were previously injected onto the model classes with ``setattr`` by
``machado.decorators``. Plain inheritance replaces that, which is what lets
``functools.cached_property`` work here: it learns its attribute name from
``__set_name__``, which Python calls only while executing a class body, so the
old ``setattr`` approach needed a hand-rolled helper to invoke it.
"""

import functools

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Value, F, Q
from django.db.models.functions import Concat

from machado import display
from machado.caching import clear_page_cache


class FeatureMixin:
    """Methods mixed onto machado.models.Feature."""

    def get_dbxrefs(self):
        """Get the feature dbxrefs."""
        result = list()
        for feature_dbxref in self.FeatureDbxref_feature_Feature.select_related(
            "dbxref__db"
        ).all():
            if feature_dbxref.dbxref.db.url:
                result.append(
                    "<a href='{}://{}{}' target='_blank'>{}:{}</a>".format(
                        feature_dbxref.dbxref.db.urlprefix,
                        feature_dbxref.dbxref.db.url,
                        feature_dbxref.dbxref.accession,
                        feature_dbxref.dbxref.db.name,
                        feature_dbxref.dbxref.accession,
                    )
                )
            else:
                result.append(
                    "{}:{}".format(
                        feature_dbxref.dbxref.db.name, feature_dbxref.dbxref.accession
                    )
                )
        return result

    def get_product(self):
        """Get the product feature prop."""
        try:
            return self.Featureprop_feature_Feature.get(
                type__name="product", type__cv__name="feature_property"
            ).value
        except ObjectDoesNotExist:
            return None

    def get_description(self):
        """Get the description feature prop."""
        try:
            return self.Featureprop_feature_Feature.get(
                type__name="description", type__cv__name="feature_property"
            ).value
        except ObjectDoesNotExist:
            return None

    def get_note(self):
        """Get the note feature prop."""
        try:
            return self.Featureprop_feature_Feature.get(
                type__name="note", type__cv__name="feature_property"
            ).value
        except ObjectDoesNotExist:
            return None

    @functools.cached_property
    def _annotation_data(self):
        """Return {"annotations": [...], "dois": {...}} for this feature."""
        rows = display.fetch_prop_rows([self.feature_id])
        return display.fetch_annotation_data(rows, [self.feature_id])[self.feature_id]

    def get_annotation(self):
        """Get the annotation feature props, each with its DOIs appended."""
        return list(self._annotation_data["annotations"])

    def get_doi(self):
        """Get the DOIs for this feature, from its pubs and its annotations."""
        return set(self._annotation_data["dois"])

    @functools.cached_property
    def _display_prop_map(self):
        """Return {type_name: [values by rank]} for this feature's props."""
        rows = display.fetch_prop_rows([self.feature_id])
        return display.group_props(rows).get(self.feature_id, {})

    def get_display(self):
        """Get the display feature prop, falling back through the chain."""
        return display.resolve_display(self._display_prop_map)

    def get_properties(self):
        """Get all the feature properties."""
        attrs_bl = ["coexpression group", "coexpression group", "annotation"]
        try:
            return (
                self.Featureprop_feature_Feature.filter(
                    type__cv__name="feature_property"
                )
                .exclude(type__name__in=attrs_bl)
                .order_by("type__name")
                .values_list("type__name", "value")
            )
        except ObjectDoesNotExist:
            return list()

    def get_synonyms(self):
        """Get all the feature synonyms."""
        result = list()
        for feature_synonym in self.FeatureSynonym_feature_Feature.select_related(
            "synonym"
        ).all():
            result.append("{}".format(feature_synonym.synonym.name))
        return result

    def get_orthologous_group(self):
        """Get the orthologous group id."""
        try:
            return self.Featureprop_feature_Feature.get(
                type__cv__name="feature_property", type__name="orthologous group"
            ).value
        except ObjectDoesNotExist:
            return None

    def get_coexpression_group(self):
        """Get the coexpression group id."""
        try:
            return self.Featureprop_feature_Feature.get(
                type__cv__name="feature_property", type__name="coexpression group"
            ).value
        except ObjectDoesNotExist:
            return None

    def get_expression_samples(self):
        """Get the expression samples and treatments."""
        try:
            return list(
                self.Analysisfeature_feature_Feature.annotate(
                    assay_name=F(
                        "analysis__Quantification_analysis_Analysis__acquisition__assay__name"
                    )
                )
                .annotate(
                    assay_description=F(
                        "analysis__Quantification_analysis_Analysis__acquisition__assay__description"
                    )
                )
                .annotate(
                    biomaterial_name=F(
                        "analysis__Quantification_analysis_Analysis__acquisition__assay__AssayBiomaterial_assay_Assay__biomaterial__name"
                    )
                )
                .annotate(
                    biomaterial_description=F(
                        "analysis__Quantification_analysis_Analysis__acquisition__assay__AssayBiomaterial_assay_Assay__biomaterial__description"
                    )
                )
                .annotate(
                    treatment_name=F(
                        "analysis__Quantification_analysis_Analysis__acquisition__assay__AssayBiomaterial_assay_Assay__biomaterial__Treatment_biomaterial_Biomaterial__name"
                    )
                )
                .filter(normscore__gt=0)
                .exclude(assay_name__isnull=True)
                .values(
                    "analysis__sourcename",
                    "normscore",
                    "assay_name",
                    "assay_description",
                    "biomaterial_name",
                    "biomaterial_description",
                    "treatment_name",
                )
            )
        except ObjectDoesNotExist:
            return None

    def get_relationship(self):
        """Get the relationships."""
        if not hasattr(settings, "MACHADO_VALID_TYPES"):
            raise AttributeError("The setting of MACHADO_VALID_TYPES is required.")

        result = list()
        feature_relationships = self.FeatureRelationship_object_Feature.select_related(
            "subject__type"
        ).filter(
            Q(type__name="part_of") | Q(type__name="translation_of"),
            type__cv__name="sequence",
        )
        for feature_relationship in feature_relationships:
            if feature_relationship.subject.type.name in settings.MACHADO_VALID_TYPES:
                result.append(feature_relationship.subject)

        feature_relationships = self.FeatureRelationship_subject_Feature.select_related(
            "object__type"
        ).filter(
            Q(type__name="part_of") | Q(type__name="translation_of"),
            type__cv__name="sequence",
        )
        for feature_relationship in feature_relationships:
            if feature_relationship.object.type.name in settings.MACHADO_VALID_TYPES:
                result.append(feature_relationship.object)

        return result

    def get_cvterm(self):
        """Get the cvterms."""
        return self.FeatureCvterm_feature_Feature.all().values(
            name=F("cvterm__name"),
            definition=F("cvterm__definition"),
            cv=F("cvterm__cv__name"),
            db=F("cvterm__dbxref__db__name"),
            dbxref=F("cvterm__dbxref__accession"),
        )

    def get_location(self):
        """Get the feature location."""
        result = list()
        for location in self.Featureloc_feature_Feature.select_related(
            "srcfeature__organism"
        ).all():
            jbrowse_url = None
            if hasattr(settings, "MACHADO_JBROWSE_URL"):
                if hasattr(settings, "MACHADO_JBROWSE_TRACKS"):
                    tracks = settings.MACHADO_JBROWSE_TRACKS
                else:
                    tracks = "ref_seq,gene,transcripts,CDS"
                if hasattr(settings, "MACHADO_JBROWSE_OFFSET"):
                    offset = settings.MACHADO_JBROWSE_OFFSET
                else:
                    offset = 1000
                if location.srcfeature is not None:
                    loc = "{}:{}..{}".format(
                        location.srcfeature.uniquename,
                        location.fmin - offset,
                        location.fmax + offset,
                    )
                    organism = "{} {}".format(
                        location.srcfeature.organism.genus,
                        location.srcfeature.organism.species,
                    )
                    if location.srcfeature.organism.infraspecific_name is not None:
                        organism += " {}".format(
                            location.srcfeature.organism.infraspecific_name
                        )
                    jbrowse_url = (
                        "{}/?data=data/{}&loc={}"
                        "&tracklist=0&nav=0&overview=0"
                        "&tracks={}".format(
                            settings.MACHADO_JBROWSE_URL, organism, loc, tracks
                        )
                    )
                    result.append(
                        {
                            "start": location.fmin,
                            "end": location.fmax,
                            "strand": location.strand,
                            "ref": location.srcfeature.uniquename,
                            "jbrowse_url": jbrowse_url,
                        }
                    )
        return result


class PubMixin:
    """Methods mixed onto machado.models.Pub."""

    def get_authors(self):
        """Get a publication string."""
        return ", ".join(
            self.Pubauthor_pub_Pub.order_by("rank")
            .annotate(author=Concat("surname", Value(" "), "givennames"))
            .values_list("author", flat=True)
        )

    @functools.cached_property
    def _doi_value(self):
        """Resolve this publication's DOI accession, or None.

        Memoized per instance because templates re-query on every mention: Django
        does not cache template method calls, and both feature.html (~line 361) and
        data-numbers.html (~line 63) mention pub.get_doi three times inside a
        per-pub loop -- data-numbers.html nests that inside a per-organism loop, so
        40 organisms x 5 pubs cost 600 queries for DOIs alone without this cache.

        .first() on an unordered queryset makes Django auto-add order_by(pk), so a
        pub carrying two DOI dbxrefs resolves to the lowest-pk one. That is the
        contract -- see the tie-break note in get_feature_annotation_data. Any
        restructuring of this query must pin the ordering explicitly.

        Staleness caveat: as with _display_prop_map and _annotation_data, the cache
        is never invalidated. A caller that adds a PubDbxref and re-reads get_doi()
        on the same in-memory Pub sees the old value; re-fetch the Pub instead.
        """
        pub_dbxref = (
            self.PubDbxref_pub_Pub.select_related("dbxref")
            .filter(dbxref__db__name="DOI")
            .first()
        )
        return pub_dbxref.dbxref.accession if pub_dbxref else None

    def get_doi(self):
        """Get the DOI of the publication."""
        return self._doi_value


class OrganismMixin:
    """Methods mixed onto machado.models.Organism."""

    @functools.cached_property
    def is_public(self):
        """Check if organism is public.

        Cached per instance. After changing visibility, call set_public (which
        invalidates the cache) or re-fetch the organism -- do not mutate the
        Organismprop row directly and expect this to notice.

        Do not annotate or assign this name. A plain property without a setter
        raises AttributeError on `organism.is_public = x`; a cached_property accepts
        it silently, and an `Organism.objects.annotate(is_public=...)` would land in
        the instance __dict__ and shadow this lookup for that instance's lifetime.
        No caller does either today -- all five filter on
        Organismprop_organism_Organism__value="false" instead.
        """
        prop = self.Organismprop_organism_Organism.filter(
            type__name="is_public", type__cv__name="organism_property"
        ).first()
        if prop:
            return prop.value != "false"
        return True

    def set_public(self, is_public: bool):
        """Set the public/private status of an organism."""
        from machado.models import Cv, Cvterm, Db, Dbxref, Organismprop

        db_local, _ = Db.objects.get_or_create(name="local")
        dbxref_is_public, _ = Dbxref.objects.get_or_create(
            db=db_local, accession="is_public"
        )
        cv_org_prop, _ = Cv.objects.get_or_create(name="organism_property")
        cvterm_is_public, _ = Cvterm.objects.get_or_create(
            cv=cv_org_prop,
            name="is_public",
            is_obsolete=0,
            is_relationshiptype=0,
            dbxref_id=dbxref_is_public.dbxref_id,
        )

        prop, created = Organismprop.objects.get_or_create(
            organism=self,
            type=cvterm_is_public,
            rank=0,
            defaults={"value": "true" if is_public else "false"},
        )
        if not created:
            prop.value = "true" if is_public else "false"
            prop.save()

        # Invalidate the cached is_public value. views/loader.py sets visibility
        # and then reads organism.is_public in the same request to build its JSON
        # response; without this the response would report the pre-change value.
        self.__dict__.pop("is_public", None)

        # Drop the rendered pages too. Visibility decides which features an
        # anonymous visitor is shown on /find/ and /data/, so every cached
        # anonymous page that counted this organism is now wrong, and the cache
        # has no expiry that would eventually correct it.
        #
        # Done here rather than in the view so that any caller changing
        # visibility is covered, not just the permissions panel. Callers
        # flipping many organisms in a loop will clear once per organism; that
        # is wasteful but not incorrect, and no caller does it today.
        clear_page_cache()
