# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Decorators."""

import functools

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Value, F, Q
from django.db.models.functions import Concat

#: Order of the display fallback chain.
DISPLAY_FALLBACK = ("display", "product", "description", "note")


def _attach_cached_property(cls, name, func):
    """Attach a cached_property to a class after class creation.

    functools.cached_property learns its attribute name via __set_name__, which
    Python calls only while executing a class body. This module patches methods
    on with setattr() afterwards, so __set_name__ must be invoked by hand or the
    first attribute access raises TypeError.
    """
    prop = functools.cached_property(func)
    prop.__set_name__(cls, name)
    setattr(cls, name, prop)


def get_feature_dbxrefs(self):
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


def get_feature_product(self):
    """Get the product feature prop."""
    try:
        return self.Featureprop_feature_Feature.get(
            type__name="product", type__cv__name="feature_property"
        ).value
    except ObjectDoesNotExist:
        return None


def get_feature_description(self):
    """Get the description feature prop."""
    try:
        return self.Featureprop_feature_Feature.get(
            type__name="description", type__cv__name="feature_property"
        ).value
    except ObjectDoesNotExist:
        return None


def get_feature_note(self):
    """Get the note feature prop."""
    try:
        return self.Featureprop_feature_Feature.get(
            type__name="note", type__cv__name="feature_property"
        ).value
    except ObjectDoesNotExist:
        return None


def get_feature_annotation_data(self):
    """Build annotations and DOIs for this feature in a fixed four queries.

    get_annotation and get_doi both walk
    Featureprop(annotation) -> FeaturepropPub -> pub DOI. Computing them
    together once removes the duplicate traversal and the per-row queries that
    the previous per-pub get_doi() calls incurred. Memoized per instance.

    Staleness caveat: because this is a cached_property, a caller that creates
    a new Featureprop or FeaturePub and then re-reads get_annotation()/get_doi()
    on this same in-memory Feature instance will see stale data -- the cache is
    never invalidated on write. No current caller does this (the loaders in
    machado/loaders/ operate on feature_id integers and never hold a live
    Feature across a write), but a future caller that does must re-fetch the
    Feature instance instead of relying on this cache surviving a write.
    """
    from machado.models import FeaturepropPub, PubDbxref

    # 1. DOIs attached directly to the feature via FeaturePub.
    direct_pub_ids = list(
        self.FeaturePub_feature_Feature.values_list("pub_id", flat=True)
    )

    # 2. Annotation props, in rank order so the output order is stable.
    prop_rows = list(
        self.Featureprop_feature_Feature.filter(
            type__name="annotation", type__cv__name="feature_property"
        )
        .order_by("rank", "featureprop_id")
        .values_list("featureprop_id", "value")
    )
    prop_ids = [prop_id for prop_id, _ in prop_rows]

    # 3. The pubs backing each annotation prop.
    pubs_by_prop = {}
    proppub_pub_ids = []
    if prop_ids:
        for prop_id, pub_id in (
            FeaturepropPub.objects.filter(featureprop_id__in=prop_ids)
            .order_by("featureprop_pub_id")
            .values_list("featureprop_id", "pub_id")
        ):
            pubs_by_prop.setdefault(prop_id, []).append(pub_id)
            proppub_pub_ids.append(pub_id)

    # 4. One DOI lookup covering both sources.
    #
    # order_by is REQUIRED for parity, not decoration. The old per-pub
    # Pub.get_doi() ended in .first(), and Django auto-adds order_by(pk) to an
    # unordered queryset for first()/last() -- so it deterministically returned
    # the lowest-pk PubDbxref. Iterating unordered here and taking the first
    # row via setdefault would instead let the query plan decide which
    # accession wins for a pub carrying two DOI dbxrefs. Ordering by the PK
    # reproduces the old choice exactly.
    #
    # No select_related: values_list() with a spanning lookup performs the join
    # itself, so select_related("dbxref") would be a no-op here.
    doi_by_pub = {}
    all_pub_ids = set(direct_pub_ids) | set(proppub_pub_ids)
    if all_pub_ids:
        for pub_id, accession in (
            PubDbxref.objects.filter(pub_id__in=all_pub_ids, dbxref__db__name="DOI")
            .order_by("pub_dbxref_id")
            .values_list("pub_id", "dbxref__accession")
        ):
            doi_by_pub.setdefault(pub_id, accession)

    annotations = []
    dois = set()
    for prop_id, value in prop_rows:
        prop_dois = [
            doi_by_pub[pub_id]
            for pub_id in pubs_by_prop.get(prop_id, ())
            if pub_id in doi_by_pub
        ]
        if prop_dois:
            annotations.append("{} (DOI:{})".format(value, ", ".join(prop_dois)))
        else:
            annotations.append(value)
        dois.update(prop_dois)

    for pub_id in direct_pub_ids:
        doi = doi_by_pub.get(pub_id)
        if doi:
            dois.add(doi)

    return {"annotations": annotations, "dois": dois}


def get_feature_annotation(self):
    """Get the annotation feature props, each with its DOIs appended."""
    return list(self._annotation_data["annotations"])


def get_feature_doi(self):
    """Get the DOIs for this feature, from its pubs and its annotations."""
    return set(self._annotation_data["dois"])


def get_feature_display_prop_map(self):
    """Return {type_name: [values by rank]} for the display fallback props.

    One query serves the whole display -> product -> description -> note chain,
    which previously cost a separate .get() per step. Memoized because
    templates commonly evaluate get_display more than once per render.
    """
    result = {}
    rows = self.Featureprop_feature_Feature.filter(
        type__cv__name="feature_property", type__name__in=DISPLAY_FALLBACK
    ).order_by("type__name", "rank")
    for type_name, value in rows.values_list("type__name", "value"):
        result.setdefault(type_name, []).append(value)
    return result


def get_feature_display(self):
    """Get the display feature prop, falling back through the chain."""
    props = self._display_prop_map
    for prop_name in DISPLAY_FALLBACK:
        values = props.get(prop_name)
        if values:
            return values[0]
    return None


def get_feature_properties(self):
    """Get all the feature properties."""
    attrs_bl = ["coexpression group", "coexpression group", "annotation"]
    try:
        return (
            self.Featureprop_feature_Feature.filter(type__cv__name="feature_property")
            .exclude(type__name__in=attrs_bl)
            .order_by("type__name")
            .values_list("type__name", "value")
        )
    except ObjectDoesNotExist:
        return list()


def get_feature_synonyms(self):
    """Get all the feature synonyms."""
    result = list()
    for feature_synonym in self.FeatureSynonym_feature_Feature.select_related(
        "synonym"
    ).all():
        result.append("{}".format(feature_synonym.synonym.name))
    return result


def get_feature_orthologous_group(self):
    """Get the orthologous group id."""
    try:
        return self.Featureprop_feature_Feature.get(
            type__cv__name="feature_property", type__name="orthologous group"
        ).value
    except ObjectDoesNotExist:
        return None


def get_feature_coexpression_group(self):
    """Get the coexpression group id."""
    try:
        return self.Featureprop_feature_Feature.get(
            type__cv__name="feature_property", type__name="coexpression group"
        ).value
    except ObjectDoesNotExist:
        return None


def get_feature_expression_samples(self):
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


def get_feature_relationship(self):
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


def get_feature_cvterm(self):
    """Get the cvterms."""
    return self.FeatureCvterm_feature_Feature.all().values(
        name=F("cvterm__name"),
        definition=F("cvterm__definition"),
        cv=F("cvterm__cv__name"),
        db=F("cvterm__dbxref__db__name"),
        dbxref=F("cvterm__dbxref__accession"),
    )


def get_feature_location(self):
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


def machado_feature_methods():
    """Add methods to machado.models.Feature."""

    def wrapper(cls):
        setattr(cls, "get_dbxrefs", get_feature_dbxrefs)
        setattr(cls, "get_display", get_feature_display)
        setattr(cls, "get_product", get_feature_product)
        setattr(cls, "get_description", get_feature_description)
        setattr(cls, "get_note", get_feature_note)
        setattr(cls, "get_annotation", get_feature_annotation)
        setattr(cls, "get_doi", get_feature_doi)
        setattr(cls, "get_orthologous_group", get_feature_orthologous_group)
        setattr(cls, "get_coexpression_group", get_feature_coexpression_group)
        setattr(cls, "get_expression_samples", get_feature_expression_samples)
        setattr(cls, "get_relationship", get_feature_relationship)
        setattr(cls, "get_cvterm", get_feature_cvterm)
        setattr(cls, "get_location", get_feature_location)
        setattr(cls, "get_properties", get_feature_properties)
        setattr(cls, "get_synonyms", get_feature_synonyms)
        _attach_cached_property(cls, "_display_prop_map", get_feature_display_prop_map)
        _attach_cached_property(cls, "_annotation_data", get_feature_annotation_data)
        return cls

    return wrapper


def get_pub_authors(self):
    """Get a publication string."""
    return ", ".join(
        self.Pubauthor_pub_Pub.order_by("rank")
        .annotate(author=Concat("surname", Value(" "), "givennames"))
        .values_list("author", flat=True)
    )


def get_pub_doi(self):
    """Get the DOI of the publication."""
    pub_dbxref = (
        self.PubDbxref_pub_Pub.select_related("dbxref")
        .filter(dbxref__db__name="DOI")
        .first()
    )
    return pub_dbxref.dbxref.accession if pub_dbxref else None


def machado_pub_methods():
    """Add methods to machado.models.Pub."""

    def wrapper(cls):
        setattr(cls, "get_authors", get_pub_authors)
        setattr(cls, "get_doi", get_pub_doi)
        return cls

    return wrapper


def get_organism_is_public(self):
    """Check if organism is public.

    Cached per instance. After changing visibility, call set_public (which
    invalidates the cache) or re-fetch the organism -- do not mutate the
    Organismprop row directly and expect this to notice.
    """
    prop = self.Organismprop_organism_Organism.filter(
        type__name="is_public", type__cv__name="organism_property"
    ).first()
    if prop:
        return prop.value != "false"
    return True


def set_organism_public(self, is_public: bool):
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


def machado_organism_methods():
    """Add methods to machado.models.Organism."""

    def wrapper(cls):
        _attach_cached_property(cls, "is_public", get_organism_is_public)
        setattr(cls, "set_public", set_organism_public)
        return cls

    return wrapper
