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

from machado.models import FeatureSearchIndex

#: Analysis programs surfaced as facets by ``_prepare_analyses``.
VALID_PROGRAMS = ["interproscan", "diamond", "blast"]

#: Featureprop type names read from the ``feature_property`` CV.
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
    """Build the organism display string for a feature."""
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
    """Assemble FeatureSearchIndex rows for a chunk. Issues no queries."""
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
