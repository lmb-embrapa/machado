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

import bisect
import dataclasses
from functools import reduce
from operator import or_

from django.conf import settings
from django.core.management.base import CommandError
from django.db.models import F, Q

from machado.models import FeatureSearchIndex

#: Analysis programs surfaced as facets by ``_prepare_analyses``.
VALID_PROGRAMS = ["interproscan", "diamond", "blast"]

# DUPLICATED LOGIC -- KEEP IN LOCKSTEP WITH machado/decorators.py.
#
# This module and ``machado.decorators`` resolve the same three things by the
# same rules, in two separate copies:
#
#   * ``DISPLAY_FALLBACK`` below            <-> ``decorators.DISPLAY_FALLBACK``
#   * ``resolve_display``                   <-> ``decorators.get_feature_display``
#   * the batching block in ``prefetch_chunk`` (steps 4-7)
#                                 <-> ``decorators.get_feature_annotation_data``
#
# ``PROP_TYPES`` is a third place that must move with them: it is the superset
# ``prefetch_chunk`` fetches, and it must contain every DISPLAY_FALLBACK name or
# ``resolve_display`` silently loses a fallback step. Change one site, change
# all of them -- the search index and the feature page are supposed to agree
# about a feature's display value and DOIs, and only these copies enforce that.
#
# This is not hypothetical drift: commit 1b4ecac added a deterministic
# ``order_by("pub_dbxref_id")`` to the DOI tie-break in ``decorators.py`` and
# missed the identical query here, so the page and the index disagreed
# nondeterministically about multi-DOI pubs until it was fixed separately.
#
# The obvious fix -- extracting the shared logic into a third module both
# import -- is not available: ``machado.models`` imports ``decorators`` at
# import time (for the method-patching decorators) and this module imports
# ``machado.models``, so ``decorators`` cannot import from here without a
# circular import. Until that cycle is broken, duplication plus this warning is
# the arrangement.

#: Featureprop type names read from the ``feature_property`` CV.
#: ``prefetch_chunk`` fetches all of these in a single query and splits them by
#: type, instead of issuing one lookup per property per feature. Defined here
#: so the contract lives beside ``resolve_display``, which depends on the
#: fallback subset. Must remain a superset of DISPLAY_FALLBACK.
PROP_TYPES = (
    "display",
    "product",
    "description",
    "note",
    "annotation",
    "orthologous group",
    "coexpression group",
)

#: Order of the display fallback chain. Twin of
#: ``machado.decorators.DISPLAY_FALLBACK``; see the lockstep warning above.
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
class IndexRunCache:
    """Memoised, chunk-independent lookups shared across one index run.

    Deliberately an object the caller creates per run rather than a
    module-level dict: a global would survive between management-command
    invocations and between tests, so a group whose membership changed (or a
    test that rolled its fixture back) would be served stale flags.
    """

    #: orthologous group value -> coexpression flag list, see
    #: ``_prefetch_orthologs_coexpression``.
    ortholog_flags: dict = dataclasses.field(default_factory=dict)


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
    """Return the display value, following the display fallback chain.

    Character-for-character twin of ``machado.decorators.get_feature_display``
    (which reads the same map off a per-instance cache instead of a chunk
    context). Change both or the feature page and the search index will report
    different display values for the same feature; see the lockstep warning at
    the top of this module for why they cannot share one implementation.

    Note the ``if values`` test: a prop that is present but whose ``value`` is
    NULL yields ``[None]``, a truthy list, so the chain STOPS there and returns
    ``None`` rather than falling through to the next prop.
    """
    for prop_name in DISPLAY_FALLBACK:
        values = props.get(prop_name)
        if values:
            return values[0]
    return None


def build_organism(organism):
    """Build the organism display string."""
    display = "{} {}".format(organism.genus, organism.species)
    if organism.infraspecific_name:
        display += " {}".format(organism.infraspecific_name)
    return display


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
        organism = build_organism(feature.organism)
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


def prefetch_chunk(feature_ids, config, cache=None):
    """Fetch all related data for a chunk of features.

    Issues a fixed number of queries regardless of how many features are in
    the chunk. Returns a :class:`ChunkContext`.

    ``cache`` is an optional :class:`IndexRunCache` shared by every chunk of
    one run; pass one to skip re-deriving the chunk-independent
    orthologs-coexpression facet for groups already seen.
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
        # order_by is REQUIRED for determinism, not decoration. A pub may carry
        # more than one DOI dbxref, and setdefault keeps whichever row arrives
        # first -- unordered, that is whatever the query plan happens to return,
        # so FeatureSearchIndex.doi (and search_vector) could flip between index
        # rebuilds and disagree with the feature page. Ordering by the PK picks
        # the lowest-pk row, matching decorators.py's get_feature_annotation_data
        # and get_pub_doi (whose .first() auto-orders by pk). See the twin-site
        # warning on DISPLAY_FALLBACK above: this query is exactly the drift that
        # warning is about -- it was missed when decorators.py was fixed.
        for row in (
            PubDbxref.objects.filter(pub_id__in=pub_ids, dbxref__db__name="DOI")
            .order_by("pub_dbxref_id")
            .values("pub_id", "dbxref__accession")
        ):
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

    # 9. match_part programs for the analyses facet.
    #
    # One query joining featureloc -> match_part feature -> analysisfeature ->
    # analysis and returning DISTINCT (srcfeature_id, program). The earlier
    # shape round-tripped one match_part feature_id per featureloc back
    # through Python into an `IN` list -- unbounded (tens of thousands of ids
    # per chunk once InterProScan/diamond data is loaded, with no dedup) and
    # only survivable because psycopg binds parameters client-side by default;
    # under `server_side_binding` it would hit libpq's 65535-parameter ceiling
    # and fail on the same chunk forever under --resume. This shape is bounded
    # by chunk_size x programs.
    #
    # `feature__organism_id=F("srcfeature__organism_id")` is the original
    # same-organism restriction, pushed into SQL; it also removes the separate
    # lookup of the source features' organism_ids.
    analysis_programs = {}
    for src, program in (
        Featureloc.objects.filter(
            srcfeature_id__in=ids,
            feature__type__name="match_part",
            feature__type__cv__name="sequence",
            feature__organism_id=F("srcfeature__organism_id"),
        )
        .values_list(
            "srcfeature_id",
            "feature__Analysisfeature_feature_Feature__analysis__program",
        )
        .distinct()
    ):
        if program is None:
            # match_part with no analysisfeature row: contributes no program,
            # and build_analyses treats a missing key as "no matches".
            continue
        analysis_programs.setdefault(src, set()).add(program)
    ctx.analysis_programs = analysis_programs

    # 10-11. relationships (both directions), filtered to valid types
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

    # 12-14. orthologs coexpression
    ctx.orthologs_coexpression = _prefetch_orthologs_coexpression(
        ids, props, ortholog_flags=None if cache is None else cache.ortholog_flags
    )

    # 15-16. overlapping features
    if config.has_overlapping:
        ctx.overlaps = _prefetch_overlaps(ids, config)

    return ctx


def _prefetch_orthologs_coexpression(ids, props, ortholog_flags=None):
    """Build the orthologs-coexpression facet for a chunk.

    The facet value depends only on the feature's orthologous group, never on
    the chunk, so ``ortholog_flags`` (see :class:`IndexRunCache`) memoises it
    per group for the lifetime of one run. Without it, a group with 500k
    members is re-expanded -- plus two ``__in`` queries over all its members
    -- once per chunk that happens to contain any of them.
    """
    groups = {}
    for fid in ids:
        values = (props.get(fid) or {}).get("orthologous group") or []
        if values:
            groups[fid] = values[0]
    if not groups:
        return {}

    if ortholog_flags is None:
        ortholog_flags = {}
    missing = {group for group in groups.values() if group not in ortholog_flags}
    if missing:
        ortholog_flags.update(_compute_ortholog_flags(missing))

    # Copy: each entry becomes a distinct FeatureSearchIndex.orthologs_coexpression
    # value and must not alias the cached list.
    return {fid: list(ortholog_flags[group]) for fid, group in groups.items()}


def _compute_ortholog_flags(distinct_groups):
    """Return ``{orthologous group: [coexpression flag, ...]}`` for the groups.

    One flag per (group member, ``translation_of`` subject of that member)
    pair, True when the subject carries a coexpression group.
    """
    from machado.models import FeatureRelationship, Featureprop

    # Ordered so a group's flag list comes out identical no matter which chunk
    # happened to populate the cache entry.
    member_rows = (
        Featureprop.objects.filter(
            type__cv__name="feature_property",
            type__name="orthologous group",
            value__in=distinct_groups,
        )
        .order_by("value", "feature_id")
        .values("feature_id", "value")
    )
    members_by_group = {group: [] for group in distinct_groups}
    for row in member_rows:
        members_by_group[row["value"]].append(row["feature_id"])

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

    flags_by_group = {}
    for group, members in members_by_group.items():
        flags = []
        for member in members:
            for subject in subjects_by_object.get(member, ()):
                flags.append(subject in coexpressed)
        flags_by_group[group] = flags
    return flags_by_group


def _prefetch_overlaps(ids, config):
    """Build the overlapping-feature keywords for a chunk.

    The coordinate window is pushed into SQL: one
    ``srcfeature_id = s AND fmin <= hi AND fmax >= lo`` predicate per
    srcfeature the chunk touches, OR-ed together (a chunk spans only one to a
    few srcfeatures, so the OR-chain stays short). That shape is what lets
    Postgres use ``featureloc_idx3 (srcfeature_id, fmin, fmax)``; filtering on
    ``srcfeature_id`` alone and applying the window in Python instead would
    pull every SNV/QTL/CNV featureloc on the whole chromosome into memory --
    millions of rows on a resequencing project -- and could not use the index.

    Candidates are then matched against the individual featurelocs of the
    chunk through a per-srcfeature list sorted by ``fmin`` plus a bisect, so
    the cost is O(m log m + matches) rather than a nested scan over every
    (own location, candidate) pair.
    """
    from machado.models import Featureloc

    own_locs = list(
        Featureloc.objects.filter(
            feature_id__in=ids,
            feature__type__name__in=config.valid_types,
            srcfeature__isnull=False,
            # NULL coordinates can never satisfy the original per-feature
            # `fmin__lte=loc.fmax, fmax__gte=loc.fmin` predicate (SQL
            # comparisons against NULL are never true), so such locations
            # contributed no keywords. Excluding them here keeps that
            # behaviour and keeps the arithmetic below NULL-free.
            fmin__isnull=False,
            fmax__isnull=False,
        ).values("feature_id", "srcfeature_id", "fmin", "fmax", "feature__type__name")
    )
    if not own_locs:
        return {}

    windows = {}
    for loc in own_locs:
        src = loc["srcfeature_id"]
        lo, hi = windows.get(src, (loc["fmin"], loc["fmax"]))
        windows[src] = (min(lo, loc["fmin"]), max(hi, loc["fmax"]))

    window_q = reduce(
        or_,
        (
            Q(srcfeature_id=src, fmin__lte=hi, fmax__gte=lo)
            for src, (lo, hi) in windows.items()
        ),
    )
    rows = (
        Featureloc.objects.filter(
            window_q, feature__type__name__in=config.overlapping_features
        )
        .values(
            "srcfeature_id",
            "fmin",
            "fmax",
            "feature__uniquename",
            "feature__name",
            "feature__type__name",
        )
        .iterator()
    )

    candidates = {}
    for row in rows:
        candidates.setdefault(row["srcfeature_id"], []).append(row)

    # Per srcfeature: candidates sorted by fmin, the parallel fmin list that
    # bisect searches, and the widest candidate span. A candidate can only
    # satisfy `fmax >= qlo` if `fmin >= qlo - widest`, so the bisect range
    # [qlo - widest, qhi] is a superset of the true matches and the exact
    # `fmax >= qlo` test inside the loop finishes the job.
    index = {}
    for src, cands in candidates.items():
        cands.sort(key=lambda row: row["fmin"])
        index[src] = (
            cands,
            [row["fmin"] for row in cands],
            max(row["fmax"] - row["fmin"] for row in cands),
        )

    overlaps = {}
    for loc in own_locs:
        entry = index.get(loc["srcfeature_id"])
        if entry is None:
            continue
        cands, fmins, widest = entry
        qlo, qhi = loc["fmin"], loc["fmax"]
        own_type = loc["feature__type__name"]
        for pos in range(
            bisect.bisect_left(fmins, qlo - widest),
            bisect.bisect_right(fmins, qhi),
        ):
            cand = cands[pos]
            if cand["fmax"] < qlo:
                continue
            if cand["feature__type__name"] == own_type:
                continue
            overlaps.setdefault(loc["feature_id"], []).append(
                (cand["feature__uniquename"], cand["feature__name"])
            )
    return overlaps
