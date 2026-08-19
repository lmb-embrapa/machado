# Copyright 2026 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Batched search-index construction.

Splits index building into two halves:

``prefetch_chunk``
    issues a fixed, small number of queries for a whole chunk of features.
``build_entries``
    a pure function that assembles ``FeatureSearchIndex`` rows from the
    prefetched data without touching the database.

Keeping the assembler pure is what makes the query count independent of the
number of features being indexed.
"""

import dataclasses

from django.conf import settings
from django.core.management.base import CommandError
from django.db.models import F, Q

from machado.models import Feature, FeatureSearchIndex

#: Analysis programs surfaced as facets by ``_prepare_analyses``.
VALID_PROGRAMS = ["interproscan", "diamond", "blast"]

#: Featureprop type names read from the ``feature_property`` CV. Consumed by
#: ``prefetch_chunk`` (added in Task 5), which fetches all of these in a single
#: query and splits them by type -- replacing what were previously several
#: separate per-feature lookups. Defined here so the contract lives beside
#: ``resolve_display``, which depends on the fallback subset.
PROP_TYPES = (
    "display",
    "product",
    "description",
    "note",
    "annotation",
    "orthologous group",
    "coexpression group",
)

#: Order of the display fallback chain.
DISPLAY_FALLBACK = ("display", "product", "description", "note")


def load_valid_programs():
    """Return the distinct analysis programs that drive the analyses facet."""
    from machado.models import Analysis

    return list(
        Analysis.objects.filter(program__in=VALID_PROGRAMS)
        .order_by("program")
        .values_list("program", flat=True)
        .distinct()
    )


def detect_overlapping(overlapping_features):
    """Return True when the corpus contains any overlapping-type feature."""
    from machado.models import Feature

    return Feature.objects.filter(type__name__in=overlapping_features).exists()


@dataclasses.dataclass(frozen=True)
class IndexConfig:
    """Settings-derived configuration for one index run."""

    valid_types: list
    overlapping_features: list
    valid_programs: list
    has_overlapping: bool

    @classmethod
    def from_settings(cls, valid_programs=None, has_overlapping=None):
        """Build a config from Django settings, measuring DB state as needed.

        Both measured values may be passed in to avoid re-querying; when
        omitted they are looked up. Raises CommandError when the required
        MACHADO_VALID_TYPES setting is absent.
        """
        try:
            valid_types = settings.MACHADO_VALID_TYPES
        except AttributeError as exc:
            raise CommandError(
                "MACHADO_VALID_TYPES is not defined in settings. " "Operation aborted."
            ) from exc
        overlapping = getattr(
            settings,
            "MACHADO_OVERLAPPING_FEATURES",
            ["SNV", "QTL", "copy_number_variation"],
        )
        if valid_programs is None:
            valid_programs = load_valid_programs()
        if has_overlapping is None:
            has_overlapping = detect_overlapping(overlapping)
        return cls(
            valid_types=list(valid_types),
            overlapping_features=list(overlapping),
            valid_programs=list(valid_programs),
            has_overlapping=has_overlapping,
        )


@dataclasses.dataclass
class ChunkContext:
    """Prefetched related data for one chunk, keyed by ``feature_id``."""

    dbxref_accessions: dict
    cvterms: dict
    protein_matches: dict
    props: dict
    annotations: dict
    dois: dict
    samples: dict
    analysis_programs: dict
    relationships: dict
    orthologs_coexpression: dict
    overlaps: dict

    @classmethod
    def empty(cls):
        """Build a context with no prefetched data."""
        return cls(
            dbxref_accessions={},
            cvterms={},
            protein_matches={},
            props={},
            annotations={},
            dois={},
            samples={},
            analysis_programs={},
            relationships={},
            orthologs_coexpression={},
            overlaps={},
        )


def resolve_display(props):
    """Return the display value, following the display fallback chain."""
    for prop_name in DISPLAY_FALLBACK:
        values = props.get(prop_name)
        if values:
            return values[0]
    return None


def build_organism(feature):
    """Build the organism display string for a feature.

    Traverses the ``organism`` FK, so the caller's queryset must have used
    ``.select_related("organism")`` for this to stay query-free.
    """
    organism = "{} {}".format(feature.organism.genus, feature.organism.species)
    if feature.organism.infraspecific_name:
        organism += " {}".format(feature.organism.infraspecific_name)
    return organism


def build_text(feature, ctx, config):
    """Aggregate every searchable keyword for a feature into one string."""
    fid = feature.feature_id
    keywords = set()

    props = ctx.props.get(fid, {})
    display = resolve_display(props)
    if display:
        keywords.add(display)

    keywords.update(ctx.dbxref_accessions.get(fid, ()))

    for db_name, accession, cvterm_name in ctx.cvterms.get(fid, ()):
        keywords.add("{}:{}".format(db_name, accession))
        keywords.add(cvterm_name)

    for uniquename, name in ctx.protein_matches.get(fid, ()):
        keywords.add(uniquename)
        if name is not None:
            keywords.add(name)

    keywords.update(ctx.annotations.get(fid, ()))
    keywords.update(ctx.dois.get(fid, ()))

    for sample in ctx.samples.get(fid, ()):
        keywords.add(sample.get("assay_name"))
        keywords.add(sample.get("biomaterial_name"))
        # `or ""` guards against NULLs from the outer joins: the original
        # code called .split() on the raw value and would raise on NULL.
        for part in (sample.get("biomaterial_description") or "").split(" "):
            keywords.add(part)
        for part in (sample.get("treatment_name") or "").split(" "):
            keywords.add(part)

    if config.has_overlapping:
        for uniquename, name in ctx.overlaps.get(fid, ()):
            keywords.add(uniquename)
            if name:
                keywords.add(name)

    if feature.name is not None:
        keywords.add(feature.name)
    keywords.add(feature.uniquename)

    keywords.discard(None)
    keywords.discard("")
    return " ".join(sorted(keywords))


def build_analyses(feature, ctx, config):
    """Build the analyses facet list for a feature."""
    programs = ctx.analysis_programs.get(feature.feature_id, set())
    result = []
    for program in config.valid_programs:
        if program in programs:
            result.append("{} matches".format(program))
        else:
            result.append("no {} matches".format(program))
    return result


def build_entries(features, ctx, config):
    """Assemble FeatureSearchIndex rows for a chunk.

    Issues no queries -- but only if the caller holds up its end of the
    bargain. This function reads ``feature.organism.*`` and
    ``feature.type.name``, which are foreign-key traversals: on a real
    ``Feature`` instance they lazily hit the database unless the queryset that
    produced it used ``.select_related("organism", "type")``. Callers MUST do
    so. Forgetting it silently reintroduces exactly the per-feature N+1 this
    whole module exists to eliminate, and no unit test using stand-in objects
    can detect it -- see ``test_build_entries_issues_no_queries``, which
    asserts zero queries against real, select_related model instances.
    """
    entries = []
    for feature in features:
        fid = feature.feature_id
        props = ctx.props.get(fid, {})
        organism = build_organism(feature)
        text = build_text(feature, ctx, config)
        display = resolve_display(props)

        ortho_values = props.get("orthologous group") or []
        coexp_values = props.get("coexpression group") or []
        ortho_group = ortho_values[0] if ortho_values else None
        coexp_group = coexp_values[0] if coexp_values else None

        samples = ctx.samples.get(fid, ())
        biomaterial = []
        treatment = []
        for sample in samples:
            desc = sample.get("biomaterial_description")
            if desc and desc not in biomaterial:
                biomaterial.append(desc)
            name = sample.get("treatment_name")
            if name and name not in treatment:
                treatment.append(name)

        entries.append(
            FeatureSearchIndex(
                feature_id=fid,
                autocomplete_text="{} {}".format(organism, text),
                organism=organism,
                so_term=feature.type.name,
                uniquename=feature.uniquename,
                name=feature.name,
                display=display,
                analyses=build_analyses(feature, ctx, config),
                doi=sorted(ctx.dois.get(fid, ())),
                biomaterial=biomaterial,
                treatment=treatment,
                orthology=bool(ortho_group),
                orthologous_group=ortho_group,
                coexpression=bool(coexp_group),
                coexpression_group=coexp_group,
                relationships=[
                    "{} {}".format(counterpart_id, type_name)
                    for counterpart_id, type_name in ctx.relationships.get(fid, ())
                ],
                orthologs_coexpression=ctx.orthologs_coexpression.get(fid, []),
            )
        )
    return entries


def _group(rows, key, value):
    """Group row dicts into ``{key: [value, ...]}``."""
    grouped = {}
    for row in rows:
        grouped.setdefault(row[key], []).append(value(row))
    return grouped


def prefetch_chunk(feature_ids, config):
    """Fetch all related data for a chunk of features.

    Issues a fixed number of queries regardless of how many features are in
    the chunk. Returns a :class:`ChunkContext`.
    """
    from machado.models import (
        Analysisfeature,
        FeatureCvterm,
        FeatureDbxref,
        FeaturePub,
        FeatureRelationship,
        Featureloc,
        Featureprop,
        FeaturepropPub,
        PubDbxref,
    )

    ctx = ChunkContext.empty()
    if not feature_ids:
        return ctx

    ids = list(feature_ids)

    # 1. dbxref accessions
    ctx.dbxref_accessions = _group(
        FeatureDbxref.objects.filter(feature_id__in=ids).values(
            "feature_id", "dbxref__accession"
        ),
        "feature_id",
        lambda r: r["dbxref__accession"],
    )

    # 2. cvterms
    ctx.cvterms = _group(
        FeatureCvterm.objects.filter(feature_id__in=ids).values(
            "feature_id",
            "cvterm__name",
            "cvterm__dbxref__accession",
            "cvterm__dbxref__db__name",
        ),
        "feature_id",
        lambda r: (
            r["cvterm__dbxref__db__name"],
            r["cvterm__dbxref__accession"],
            r["cvterm__name"],
        ),
    )

    # 3. protein_match hits
    ctx.protein_matches = _group(
        FeatureRelationship.objects.filter(
            object_id__in=ids,
            subject__type__name="protein_match",
            subject__type__cv__name="sequence",
        )
        .order_by("subject__uniquename")
        .values("object_id", "subject__uniquename", "subject__name"),
        "object_id",
        lambda r: (r["subject__uniquename"], r["subject__name"]),
    )

    # 4. feature properties (one query serves seven prop types)
    prop_rows = list(
        Featureprop.objects.filter(
            feature_id__in=ids,
            type__cv__name="feature_property",
            type__name__in=PROP_TYPES,
        )
        .order_by("feature_id", "type__name", "rank")
        .values("featureprop_id", "feature_id", "type__name", "value")
    )
    props = {}
    for row in prop_rows:
        by_type = props.setdefault(row["feature_id"], {})
        by_type.setdefault(row["type__name"], []).append(row["value"])
    ctx.props = props

    # 5-7. annotation DOIs and publication DOIs share one PubDbxref lookup
    annotation_rows = [r for r in prop_rows if r["type__name"] == "annotation"]
    annotation_ids = [r["featureprop_id"] for r in annotation_rows]

    proppub_rows = (
        list(
            FeaturepropPub.objects.filter(featureprop_id__in=annotation_ids)
            .order_by("featureprop_id", "pub_id")
            .values("featureprop_id", "pub_id")
        )
        if annotation_ids
        else []
    )

    featurepub_rows = list(
        FeaturePub.objects.filter(feature_id__in=ids)
        .order_by("feature_id", "pub_id")
        .values("feature_id", "pub_id")
    )

    pub_ids = {r["pub_id"] for r in proppub_rows}
    pub_ids.update(r["pub_id"] for r in featurepub_rows)
    pub_doi = {}
    if pub_ids:
        for row in PubDbxref.objects.filter(
            pub_id__in=pub_ids, dbxref__db__name="DOI"
        ).values("pub_id", "dbxref__accession"):
            pub_doi.setdefault(row["pub_id"], row["dbxref__accession"])

    proppub_by_prop = {}
    for row in proppub_rows:
        proppub_by_prop.setdefault(row["featureprop_id"], []).append(row["pub_id"])

    annotations = {}
    dois = {}
    for row in annotation_rows:
        fid = row["feature_id"]
        prop_dois = [
            pub_doi[pid]
            for pid in proppub_by_prop.get(row["featureprop_id"], [])
            if pid in pub_doi
        ]
        if prop_dois:
            label = "{} (DOI:{})".format(row["value"], ", ".join(prop_dois))
        else:
            label = row["value"]
        annotations.setdefault(fid, []).append(label)
        dois.setdefault(fid, set()).update(prop_dois)

    for row in featurepub_rows:
        doi = pub_doi.get(row["pub_id"])
        if doi:
            dois.setdefault(row["feature_id"], set()).add(doi)

    ctx.annotations = annotations
    ctx.dois = dois

    # 8. expression samples - the 6-table join, once per chunk
    ctx.samples = _group(
        Analysisfeature.objects.filter(feature_id__in=ids)
        .annotate(
            assay_name=F(
                "analysis__Quantification_analysis_Analysis__acquisition"
                "__assay__name"
            ),
            assay_description=F(
                "analysis__Quantification_analysis_Analysis__acquisition"
                "__assay__description"
            ),
            biomaterial_name=F(
                "analysis__Quantification_analysis_Analysis__acquisition"
                "__assay__AssayBiomaterial_assay_Assay__biomaterial__name"
            ),
            biomaterial_description=F(
                "analysis__Quantification_analysis_Analysis__acquisition"
                "__assay__AssayBiomaterial_assay_Assay__biomaterial"
                "__description"
            ),
            treatment_name=F(
                "analysis__Quantification_analysis_Analysis__acquisition"
                "__assay__AssayBiomaterial_assay_Assay__biomaterial"
                "__Treatment_biomaterial_Biomaterial__name"
            ),
        )
        .filter(normscore__gt=0)
        .exclude(assay_name__isnull=True)
        .order_by("feature_id")
        .values(
            "feature_id",
            "analysis__sourcename",
            "normscore",
            "assay_name",
            "assay_description",
            "biomaterial_name",
            "biomaterial_description",
            "treatment_name",
        ),
        "feature_id",
        lambda r: r,
    )

    # 9-10. match_part programs for the analyses facet
    match_part_rows = list(
        Featureloc.objects.filter(
            srcfeature_id__in=ids,
            feature__type__name="match_part",
            feature__type__cv__name="sequence",
        ).values("srcfeature_id", "feature_id", "feature__organism_id")
    )
    src_organism = dict(
        (f_id, org_id)
        for f_id, org_id in Feature.objects.filter(feature_id__in=ids).values_list(
            "feature_id", "organism_id"
        )
    )
    match_part_ids = [r["feature_id"] for r in match_part_rows]
    program_by_match_part = {}
    if match_part_ids:
        for row in Analysisfeature.objects.filter(feature_id__in=match_part_ids).values(
            "feature_id", "analysis__program"
        ):
            program_by_match_part.setdefault(row["feature_id"], set()).add(
                row["analysis__program"]
            )

    analysis_programs = {}
    for row in match_part_rows:
        src = row["srcfeature_id"]
        # preserve the original same-organism restriction
        if row["feature__organism_id"] != src_organism.get(src):
            continue
        analysis_programs.setdefault(src, set()).update(
            program_by_match_part.get(row["feature_id"], ())
        )
    ctx.analysis_programs = analysis_programs

    # 11. relationships (both directions), filtered to valid types
    relationships = {}
    rel_filter = Q(type__name="part_of") | Q(type__name="translation_of")
    for row in (
        FeatureRelationship.objects.filter(
            rel_filter, type__cv__name="sequence", object_id__in=ids
        )
        .order_by("object_id", "subject_id")
        .values("object_id", "subject_id", "subject__type__name")
    ):
        if row["subject__type__name"] in config.valid_types:
            relationships.setdefault(row["object_id"], []).append(
                (row["subject_id"], row["subject__type__name"])
            )
    for row in (
        FeatureRelationship.objects.filter(
            rel_filter, type__cv__name="sequence", subject_id__in=ids
        )
        .order_by("subject_id", "object_id")
        .values("subject_id", "object_id", "object__type__name")
    ):
        if row["object__type__name"] in config.valid_types:
            relationships.setdefault(row["subject_id"], []).append(
                (row["object_id"], row["object__type__name"])
            )
    ctx.relationships = relationships

    # 12. orthologs coexpression
    ctx.orthologs_coexpression = _prefetch_orthologs_coexpression(ids, props)

    # 13. overlapping features
    if config.has_overlapping:
        ctx.overlaps = _prefetch_overlaps(ids, config)

    return ctx


def _prefetch_orthologs_coexpression(ids, props):
    """Build the orthologs-coexpression facet for a chunk."""
    from machado.models import FeatureRelationship, Featureprop

    groups = {}
    for fid in ids:
        values = (props.get(fid) or {}).get("orthologous group") or []
        if values:
            groups[fid] = values[0]
    if not groups:
        return {}

    distinct_groups = set(groups.values())
    members_by_group = {}
    for row in Featureprop.objects.filter(
        type__cv__name="feature_property",
        type__name="orthologous group",
        value__in=distinct_groups,
    ).values("feature_id", "value"):
        members_by_group.setdefault(row["value"], []).append(row["feature_id"])

    all_members = [m for ms in members_by_group.values() for m in ms]
    subjects_by_object = {}
    if all_members:
        for row in (
            FeatureRelationship.objects.filter(
                type__name="translation_of", object_id__in=all_members
            )
            .order_by("object_id", "subject_id")
            .values("object_id", "subject_id")
        ):
            subjects_by_object.setdefault(row["object_id"], []).append(
                row["subject_id"]
            )

    subject_ids = [s for ss in subjects_by_object.values() for s in ss]
    coexpressed = set()
    if subject_ids:
        coexpressed = set(
            Featureprop.objects.filter(
                type__cv__name="feature_property",
                type__name="coexpression group",
                feature_id__in=subject_ids,
            ).values_list("feature_id", flat=True)
        )

    result = {}
    for fid, group in groups.items():
        flags = []
        for member in members_by_group.get(group, ()):
            for subject in subjects_by_object.get(member, ()):
                flags.append(subject in coexpressed)
        result[fid] = flags
    return result


def _prefetch_overlaps(ids, config):
    """Build the overlapping-feature keywords for a chunk.

    The overlap query is bounded by the coordinate window actually spanned by
    this chunk, not by the whole source feature, so memory stays proportional
    to the chunk rather than to chromosome size.
    """
    from machado.models import Featureloc

    own_locs = list(
        Featureloc.objects.filter(
            feature_id__in=ids,
            feature__type__name__in=config.valid_types,
            srcfeature__isnull=False,
        ).values("feature_id", "srcfeature_id", "fmin", "fmax", "feature__type__name")
    )
    if not own_locs:
        return {}

    windows = {}
    for loc in own_locs:
        src = loc["srcfeature_id"]
        lo, hi = windows.get(src, (loc["fmin"], loc["fmax"]))
        windows[src] = (min(lo, loc["fmin"]), max(hi, loc["fmax"]))

    candidates = {}
    for src, (lo, hi) in windows.items():
        candidates[src] = []
    rows = Featureloc.objects.filter(
        srcfeature_id__in=list(windows),
        feature__type__name__in=config.overlapping_features,
    ).values(
        "srcfeature_id",
        "fmin",
        "fmax",
        "feature__uniquename",
        "feature__name",
        "feature__type__name",
    )
    for row in rows:
        lo, hi = windows[row["srcfeature_id"]]
        if row["fmax"] >= lo and row["fmin"] <= hi:
            candidates[row["srcfeature_id"]].append(row)

    overlaps = {}
    for loc in own_locs:
        for cand in candidates.get(loc["srcfeature_id"], ()):
            if cand["feature__type__name"] == loc["feature__type__name"]:
                continue
            if cand["fmax"] >= loc["fmin"] and cand["fmin"] <= loc["fmax"]:
                overlaps.setdefault(loc["feature_id"], []).append(
                    (cand["feature__uniquename"], cand["feature__name"])
                )
    return overlaps
