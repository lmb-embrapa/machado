# Copyright 2026 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Shared real-data fixture for decorators tests.

The decorator methods in machado/decorators.py are query-heavy helpers. Testing
them against MagicMock querysets cannot detect an N+1, because a mock has no
query count. This fixture builds real rows so ``assertNumQueries`` can be used,
and provides ``add_*`` helpers so a test can prove a query count is invariant to
row count rather than merely low.
"""

from types import SimpleNamespace

from machado.models import (
    Cv,
    Cvterm,
    Db,
    Dbxref,
    Feature,
    FeatureDbxref,
    FeaturePub,
    FeatureRelationship,
    FeatureSynonym,
    Featureloc,
    Featureprop,
    FeaturepropPub,
    Organism,
    Organismprop,
    Pub,
    PubDbxref,
    Synonym,
)

TS = "2023-01-01T00:00:00Z"


def _cvterm(cv, db, name, accession=None):
    """Create a Cvterm with its own Dbxref."""
    dbxref = Dbxref.objects.create(db=db, accession=accession or name, version="1")
    return Cvterm.objects.create(
        name=name, cv=cv, dbxref=dbxref, is_obsolete=0, is_relationshiptype=0
    )


def _feature(organism, cvterm, uniquename, name=None):
    """Create a Feature with the mandatory audit fields."""
    return Feature.objects.create(
        organism=organism,
        uniquename=uniquename,
        name=name,
        type=cvterm,
        is_analysis=False,
        is_obsolete=False,
        timeaccessioned=TS,
        timelastmodified=TS,
    )


def _pub_with_doi(fx, uniquename, accession):
    """Create a Pub carrying a DOI dbxref."""
    pub = Pub.objects.create(uniquename=uniquename, type=fx.t_journal, title="T")
    dbxref = Dbxref.objects.create(db=fx.db_doi, accession=accession, version="1")
    PubDbxref.objects.create(pub=pub, dbxref=dbxref, is_current=True)
    return pub


def build_decorator_fixture():
    """Build the corpus and return a namespace of the created objects."""
    fx = SimpleNamespace()

    # ── vocabularies ─────────────────────────────────────────────────────
    fx.db_with_url = Db.objects.create(
        name="URLDB", url="www.example.com/", urlprefix="https"
    )
    fx.db_plain = Db.objects.create(name="PlainDB")
    fx.db_doi = Db.objects.create(name="DOI")
    fx.db_local = Db.objects.create(name="local")

    cv_seq = Cv.objects.create(name="sequence")
    cv_prop = Cv.objects.create(name="feature_property")
    cv_syn = Cv.objects.create(name="synonym_type")
    cv_pub = Cv.objects.create(name="pub_type")
    cv_org = Cv.objects.create(name="organism_property")

    fx.t_gene = _cvterm(cv_seq, fx.db_local, "gene")
    fx.t_mrna = _cvterm(cv_seq, fx.db_local, "mRNA")
    fx.t_polypeptide = _cvterm(cv_seq, fx.db_local, "polypeptide")
    fx.t_chromosome = _cvterm(cv_seq, fx.db_local, "chromosome")
    fx.t_part_of = _cvterm(cv_seq, fx.db_local, "part_of")
    fx.t_translation_of = _cvterm(cv_seq, fx.db_local, "translation_of")

    fx.p_display = _cvterm(cv_prop, fx.db_local, "display")
    fx.p_product = _cvterm(cv_prop, fx.db_local, "product")
    fx.p_description = _cvterm(cv_prop, fx.db_local, "description")
    fx.p_note = _cvterm(cv_prop, fx.db_local, "note")
    fx.p_annotation = _cvterm(cv_prop, fx.db_local, "annotation")

    fx.t_symbol = _cvterm(cv_syn, fx.db_local, "symbol")
    fx.t_journal = _cvterm(cv_pub, fx.db_local, "journal")
    fx.p_is_public = _cvterm(cv_org, fx.db_local, "is_public")

    # ── organism and features ────────────────────────────────────────────
    fx.organism = Organism.objects.create(genus="Arabidopsis", species="thaliana")
    fx.gene = _feature(fx.organism, fx.t_gene, "GENE_A", "GeneAlpha")
    fx.mrna = _feature(fx.organism, fx.t_mrna, "MRNA_A", "mRnaAlpha")
    fx.polypeptide = _feature(fx.organism, fx.t_polypeptide, "POLY_A", "PolyAlpha")
    fx.chromosome = _feature(fx.organism, fx.t_chromosome, "CHR1")

    # ── publications ─────────────────────────────────────────────────────
    fx.pub_with_doi = _pub_with_doi(fx, "PUB:1", "10.1234/one")
    fx.pub_second_doi = _pub_with_doi(fx, "PUB:2", "10.1234/two")
    fx.pub_without_doi = Pub.objects.create(
        uniquename="PUB:3", type=fx.t_journal, title="NoDoi"
    )
    # A DOI reachable ONLY through a direct FeaturePub, never through an
    # annotation. Without it, get_doi's union of its two sources cannot be
    # tested: if both sources carried the same accessions, dropping one
    # entirely would leave the result unchanged and the test would still pass.
    fx.pub_featurepub_only_doi = _pub_with_doi(fx, "PUB:4", "10.1234/three")

    # ── dbxrefs: one on a URL db, one on a plain db ──────────────────────
    d1 = Dbxref.objects.create(db=fx.db_with_url, accession="12345", version="1")
    FeatureDbxref.objects.create(feature=fx.gene, dbxref=d1, is_current=True)
    d2 = Dbxref.objects.create(db=fx.db_plain, accession="67890", version="1")
    FeatureDbxref.objects.create(feature=fx.gene, dbxref=d2, is_current=True)

    # ── synonyms ─────────────────────────────────────────────────────────
    add_synonyms(fx, fx.gene, 2)

    # ── relationships: two valid types plus one invalid, both directions ─
    FeatureRelationship.objects.create(
        subject=fx.mrna, object=fx.gene, type=fx.t_part_of, rank=0
    )
    FeatureRelationship.objects.create(
        subject=fx.chromosome, object=fx.gene, type=fx.t_part_of, rank=0
    )
    FeatureRelationship.objects.create(
        subject=fx.gene, object=fx.polypeptide, type=fx.t_translation_of, rank=0
    )

    # ── locations: one located, one with a NULL srcfeature ───────────────
    Featureloc.objects.create(
        feature=fx.gene,
        srcfeature=fx.chromosome,
        fmin=100,
        fmax=200,
        is_fmin_partial=False,
        is_fmax_partial=False,
        locgroup=0,
        rank=0,
    )
    Featureloc.objects.create(
        feature=fx.gene,
        srcfeature=None,
        fmin=None,
        fmax=None,
        is_fmin_partial=False,
        is_fmax_partial=False,
        locgroup=0,
        rank=1,
    )

    # ── props: display on the gene; product-only on the mrna ────────────
    Featureprop.objects.create(
        feature=fx.gene, type=fx.p_display, value="alpha kinase", rank=0
    )
    Featureprop.objects.create(
        feature=fx.mrna, type=fx.p_product, value="the product", rank=0
    )

    # ── annotations with DOIs, plus direct FeaturePub DOIs ──────────────
    # add_annotations attaches pub_with_doi + pub_second_doi, i.e. {one, two}.
    # The direct FeaturePub deliberately uses a THIRD accession so that
    # get_doi's union of its two sources is actually observable.
    add_annotations(fx, fx.gene, 2)
    FeaturePub.objects.create(feature=fx.gene, pub=fx.pub_featurepub_only_doi)
    FeaturePub.objects.create(feature=fx.gene, pub=fx.pub_without_doi)

    # ── organism visibility prop ────────────────────────────────────────
    Organismprop.objects.create(
        organism=fx.organism, type=fx.p_is_public, value="true", rank=0
    )

    return fx


def add_dbxrefs(fx, feature, n):
    """Attach n extra dbxrefs on the plain db, for invariance testing."""
    for i in range(n):
        dbxref = Dbxref.objects.create(
            db=fx.db_plain, accession="extra_{}".format(i), version="1"
        )
        FeatureDbxref.objects.create(feature=feature, dbxref=dbxref, is_current=True)


def add_synonyms(fx, feature, n):
    """Attach n synonyms, for invariance testing."""
    existing = FeatureSynonym.objects.filter(feature=feature).count()
    for i in range(n):
        label = "syn_{}".format(existing + i)
        synonym = Synonym.objects.create(
            name=label, type=fx.t_symbol, synonym_sgml=label
        )
        FeatureSynonym.objects.create(
            synonym=synonym,
            feature=feature,
            pub=fx.pub_with_doi,
            is_current=True,
            is_internal=False,
        )


def add_locations(fx, feature, n):
    """Attach n extra located Featurelocs, for invariance testing."""
    base = Featureloc.objects.filter(feature=feature).count()
    for i in range(n):
        Featureloc.objects.create(
            feature=feature,
            srcfeature=fx.chromosome,
            fmin=1000 + i * 10,
            fmax=1005 + i * 10,
            is_fmin_partial=False,
            is_fmax_partial=False,
            locgroup=0,
            rank=base + i,
        )


def add_annotations(fx, feature, n, with_doi=True):
    """Attach n annotation props, each optionally carrying two DOI'd pubs."""
    base = Featureprop.objects.filter(feature=feature, type=fx.p_annotation).count()
    for i in range(n):
        prop = Featureprop.objects.create(
            feature=feature,
            type=fx.p_annotation,
            value="annotation {}".format(base + i),
            rank=base + i,
        )
        if with_doi:
            FeaturepropPub.objects.create(featureprop=prop, pub=fx.pub_with_doi)
            FeaturepropPub.objects.create(featureprop=prop, pub=fx.pub_second_doi)
