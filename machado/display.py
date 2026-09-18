# Copyright 2026 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Display-value and annotation/DOI resolution, shared by two call sites.

``machado.mixins.FeatureMixin`` resolves these for one feature at a time and
``machado.searchindex.prefetch_chunk`` for a whole chunk; both go through the
functions here, so the feature page and the search index cannot disagree about
a feature's display value or its DOIs.

DO NOT IMPORT ``machado.models`` AT MODULE SCOPE. ``machado.models`` imports
``machado.mixins``, which imports this module, and ``machado.searchindex``
imports ``machado.models``. Deferring every model import into a function body
is what keeps that from being a cycle -- and the cycle is precisely why this
logic used to exist in two hand-synchronised copies.
"""

#: Featureprop type names read from the ``feature_property`` CV. Fetched in one
#: query and split by type rather than one lookup per property per feature.
#: Must remain a superset of DISPLAY_FALLBACK; asserted below.
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

assert set(DISPLAY_FALLBACK) <= set(PROP_TYPES), (
    "DISPLAY_FALLBACK must be a subset of PROP_TYPES, or the fetched rows "
    "silently lose a fallback step"
)


def resolve_display(props):
    """Return the display value for one feature, following the fallback chain.

    ``props`` is one feature's entry from :func:`group_props`.

    Note the ``if values`` test rather than ``is not None``. ``Featureprop.value``
    is a nullable TextField and ``Feature`` is ``managed = False``, so other GMOD
    tooling can write a prop row whose value is NULL. Such a row arrives here as
    ``[None]`` -- a truthy list -- so the chain STOPS and this returns ``None``
    rather than falling through to the next name.
    """
    for prop_name in DISPLAY_FALLBACK:
        values = props.get(prop_name)
        if values:
            return values[0]
    return None


def format_annotation(value, dois):
    """Render one annotation, appending its DOIs when it has any."""
    if dois:
        return "{} (DOI:{})".format(value, ", ".join(dois))
    return value


def fetch_prop_rows(feature_ids):
    """Fetch every PROP_TYPES prop for these features in one query.

    The ``featureprop_id`` tie-break after ``rank`` is required, not decoration:
    without it two props at the same rank order by whatever the query plan
    returns, so a feature with two same-rank annotations renders them in an
    unstable order.
    """
    from machado.models import Featureprop

    ids = list(feature_ids)
    if not ids:
        return []
    return list(
        Featureprop.objects.filter(
            feature_id__in=ids,
            type__cv__name="feature_property",
            type__name__in=PROP_TYPES,
        )
        .order_by("feature_id", "type__name", "rank", "featureprop_id")
        .values("featureprop_id", "feature_id", "type__name", "value")
    )


def group_props(prop_rows):
    """Split fetched rows into ``{feature_id: {type_name: [values by rank]}}``."""
    grouped = {}
    for row in prop_rows:
        by_type = grouped.setdefault(row["feature_id"], {})
        by_type.setdefault(row["type__name"], []).append(row["value"])
    return grouped


def fetch_pub_doi_map(pub_ids):
    """Resolve ``{pub_id: DOI accession}`` for these pubs in one query.

    ``order_by`` is required for determinism, not decoration. A pub may carry
    more than one DOI dbxref and ``setdefault`` keeps whichever row arrives
    first; unordered, that is whatever the query plan returns, so the stored
    index value could flip between rebuilds. Ordering by the PK picks the
    lowest-pk row, which is also what ``Pub.get_doi``'s ``.first()`` resolves to
    (Django auto-adds ``order_by(pk)`` to an unordered ``first()``).
    """
    from machado.models import PubDbxref

    doi_by_pub = {}
    ids = list(pub_ids)
    if not ids:
        return doi_by_pub
    for row in (
        PubDbxref.objects.filter(pub_id__in=ids, dbxref__db__name="DOI")
        .order_by("pub_dbxref_id")
        .values("pub_id", "dbxref__accession")
    ):
        doi_by_pub.setdefault(row["pub_id"], row["dbxref__accession"])
    return doi_by_pub


def fetch_annotation_data(prop_rows, feature_ids):
    """Build annotations and DOIs for these features in three queries.

    ``prop_rows`` comes from :func:`fetch_prop_rows`; the annotation props are
    filtered out of it rather than re-queried, which is what keeps the total
    fixed at three queries here regardless of how many features or annotations
    are involved.

    Returns ``{feature_id: {"annotations": [...], "dois": {...}}}``, with an
    entry for every id in ``feature_ids``.
    """
    from machado.models import FeaturePub, FeaturepropPub

    ids = list(feature_ids)
    result = {fid: {"annotations": [], "dois": set()} for fid in ids}
    if not ids:
        return result

    annotation_rows = [r for r in prop_rows if r["type__name"] == "annotation"]
    annotation_ids = [r["featureprop_id"] for r in annotation_rows]

    # Ordered by its own PK so the DOIs within one annotation render in a
    # stable order. Ordering by pub_id instead would be equally stable but
    # would differ from what the feature page has always shown.
    proppub_rows = (
        list(
            FeaturepropPub.objects.filter(featureprop_id__in=annotation_ids)
            .order_by("featureprop_pub_id")
            .values("featureprop_id", "pub_id")
        )
        if annotation_ids
        else []
    )

    featurepub_rows = list(
        FeaturePub.objects.filter(feature_id__in=ids)
        .order_by("feature_pub_id")
        .values("feature_id", "pub_id")
    )

    pub_ids = {r["pub_id"] for r in proppub_rows}
    pub_ids.update(r["pub_id"] for r in featurepub_rows)
    doi_by_pub = fetch_pub_doi_map(pub_ids)

    pubs_by_prop = {}
    for row in proppub_rows:
        pubs_by_prop.setdefault(row["featureprop_id"], []).append(row["pub_id"])

    for row in annotation_rows:
        entry = result.setdefault(row["feature_id"], {"annotations": [], "dois": set()})
        # Truthiness, not membership. Dbxref.accession is non-null but may
        # legitimately be ''; testing `pub_id in doi_by_pub` instead would
        # render "my annotation (DOI:)".
        prop_dois = [
            doi
            for doi in (
                doi_by_pub.get(pub_id)
                for pub_id in pubs_by_prop.get(row["featureprop_id"], ())
            )
            if doi
        ]
        entry["annotations"].append(format_annotation(row["value"], prop_dois))
        entry["dois"].update(prop_dois)

    for row in featurepub_rows:
        doi = doi_by_pub.get(row["pub_id"])
        if doi:
            result.setdefault(row["feature_id"], {"annotations": [], "dois": set()})[
                "dois"
            ].add(doi)

    return result
