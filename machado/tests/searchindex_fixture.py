# Copyright 2026 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Shared fixture builder for search-index tests.

Builds a small corpus that exercises every branch of the index builder:
dbxrefs, cvterms, annotation props with DOIs, publication DOIs, expression
samples, part_of/translation_of relationships, orthologous and coexpression
groups, and an overlapping-feature case.
"""

from machado.models import (
    Analysis,
    Analysisfeature,
    Acquisition,
    Arraydesign,
    Assay,
    AssayBiomaterial,
    Biomaterial,
    Contact,
    Cv,
    Cvterm,
    Db,
    Dbxref,
    Feature,
    FeatureCvterm,
    FeatureDbxref,
    FeaturePub,
    FeatureRelationship,
    Featureloc,
    Featureprop,
    FeaturepropPub,
    Organism,
    Pub,
    PubDbxref,
    Quantification,
    Treatment,
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


def build_search_index_fixture():
    """Build the corpus and return a label -> Feature mapping."""
    db_local = Db.objects.create(name="local")
    db_go = Db.objects.create(name="GO")
    db_doi = Db.objects.create(name="DOI")

    cv_seq = Cv.objects.create(name="sequence")
    cv_prop = Cv.objects.create(name="feature_property")
    cv_go = Cv.objects.create(name="biological_process")
    cv_pub = Cv.objects.create(name="pub_type")
    cv_null = Cv.objects.create(name="null")

    t_gene = _cvterm(cv_seq, db_local, "gene")
    t_mrna = _cvterm(cv_seq, db_local, "mRNA")
    t_poly = _cvterm(cv_seq, db_local, "polypeptide")
    t_pmatch = _cvterm(cv_seq, db_local, "protein_match")
    t_snv = _cvterm(cv_seq, db_local, "SNV")
    t_chrom = _cvterm(cv_seq, db_local, "chromosome")
    t_part_of = _cvterm(cv_seq, db_local, "part_of")
    t_translation_of = _cvterm(cv_seq, db_local, "translation_of")

    p_display = _cvterm(cv_prop, db_local, "display")
    p_product = _cvterm(cv_prop, db_local, "product")
    p_annotation = _cvterm(cv_prop, db_local, "annotation")
    p_ortho = _cvterm(cv_prop, db_local, "orthologous group")
    p_coexp = _cvterm(cv_prop, db_local, "coexpression group")

    go_term = _cvterm(cv_go, db_go, "transmembrane transport", "0055085")
    pub_type = _cvterm(cv_pub, db_local, "journal")

    # "null" platform type, used only to satisfy Assay/Arraydesign's
    # required FKs -- mirrors machado.loaders.assay.AssayLoader.__init__,
    # which does the same thing because real loaders never have a real
    # arraydesign/operator to hand either.
    t_null = _cvterm(cv_null, db_local, "null")

    organism = Organism.objects.create(
        genus="Arabidopsis", species="thaliana", common_name="thale cress"
    )

    # ── publication with a DOI ───────────────────────────────────────────
    pub = Pub.objects.create(uniquename="PUB:1", type=pub_type, title="A Paper")
    doi_dbxref = Dbxref.objects.create(
        db=db_doi, accession="10.1234/parity", version="1"
    )
    PubDbxref.objects.create(pub=pub, dbxref=doi_dbxref, is_current=True)

    features = {}

    # ── feature A: the fully-loaded case ─────────────────────────────────
    gene_a = _feature(organism, t_gene, "GENE_A", "GeneAlpha")
    features["gene_a"] = gene_a

    Featureprop.objects.create(
        feature=gene_a, type=p_display, value="alpha kinase", rank=0
    )
    Featureprop.objects.create(feature=gene_a, type=p_ortho, value="OG_1", rank=0)
    Featureprop.objects.create(feature=gene_a, type=p_coexp, value="CG_1", rank=0)

    annot = Featureprop.objects.create(
        feature=gene_a, type=p_annotation, value="catalytic activity", rank=0
    )
    FeaturepropPub.objects.create(featureprop=annot, pub=pub)
    FeaturePub.objects.create(feature=gene_a, pub=pub)

    acc_dbxref = Dbxref.objects.create(db=db_local, accession="ACC_A", version="1")
    FeatureDbxref.objects.create(feature=gene_a, dbxref=acc_dbxref, is_current=True)
    FeatureCvterm.objects.create(
        feature=gene_a, cvterm=go_term, pub=pub, is_not=False, rank=0
    )

    # protein_match hit on gene_a
    pmatch = _feature(organism, t_pmatch, "PMATCH_A", "PfamHit")
    FeatureRelationship.objects.create(
        subject=pmatch, object=gene_a, type=t_part_of, rank=0
    )

    # part_of child (mRNA) -> shows up in relationships
    mrna_a = _feature(organism, t_mrna, "MRNA_A", "mRnaAlpha")
    features["mrna_a"] = mrna_a
    FeatureRelationship.objects.create(
        subject=mrna_a, object=gene_a, type=t_part_of, rank=0
    )

    # translation_of polypeptide for the ortholog/coexpression path
    poly_a = _feature(organism, t_poly, "POLY_A", "PolyAlpha")
    Featureprop.objects.create(feature=poly_a, type=p_ortho, value="OG_1", rank=0)
    FeatureRelationship.objects.create(
        subject=mrna_a, object=poly_a, type=t_translation_of, rank=0
    )
    Featureprop.objects.create(feature=mrna_a, type=p_coexp, value="CG_1", rank=0)

    # ── expression samples for gene_a ────────────────────────────────────
    analysis_rna = Analysis.objects.create(
        program="rnaseq",
        programversion="1.0",
        sourcename="SRR_ALPHA",
        timeexecuted=TS,
    )
    # Assay requires arraydesign and operator FKs (no blank=True/null=True
    # in this chado revision). Real loaders (machado.loaders.assay
    # .AssayLoader) hit the same requirement and solve it with a "null"
    # Contact/Arraydesign pair when there is no real one to hand -- do the
    # same here.
    contact_null = Contact.objects.create(name="null contact")
    arraydesign_null = Arraydesign.objects.create(
        manufacturer=contact_null, platformtype=t_null, name="null arraydesign"
    )
    assay = Assay.objects.create(
        name="assay_alpha",
        description="alpha assay",
        arraydesign=arraydesign_null,
        operator=contact_null,
    )
    biomaterial = Biomaterial.objects.create(
        name="bio_alpha", description="leaf tissue sample"
    )
    AssayBiomaterial.objects.create(assay=assay, biomaterial=biomaterial, rank=0)
    Treatment.objects.create(
        biomaterial=biomaterial, type=p_product, name="drought stress", rank=0
    )
    acquisition = Acquisition.objects.create(assay=assay)
    Quantification.objects.create(acquisition=acquisition, analysis=analysis_rna)
    Analysisfeature.objects.create(feature=gene_a, analysis=analysis_rna, normscore=5.0)

    # ── match_part + blast analysis for _prepare_analyses ────────────────
    analysis_blast = Analysis.objects.create(
        program="blast", programversion="2.0", timeexecuted=TS
    )
    t_match_part = _cvterm(cv_seq, db_local, "match_part")
    match_part = _feature(organism, t_match_part, "MP_A")
    Featureloc.objects.create(
        feature=match_part,
        srcfeature=gene_a,
        fmin=10,
        fmax=20,
        is_fmin_partial=False,
        is_fmax_partial=False,
        locgroup=0,
        rank=0,
    )
    Analysisfeature.objects.create(
        feature=match_part, analysis=analysis_blast, normscore=1.0
    )

    # ── overlapping feature case ─────────────────────────────────────────
    chrom = _feature(organism, t_chrom, "CHR1")
    Featureloc.objects.create(
        feature=gene_a,
        srcfeature=chrom,
        fmin=100,
        fmax=200,
        is_fmin_partial=False,
        is_fmax_partial=False,
        locgroup=0,
        rank=0,
    )
    snv = _feature(organism, t_snv, "SNV_1", "rs123")
    Featureloc.objects.create(
        feature=snv,
        srcfeature=chrom,
        fmin=150,
        fmax=151,
        is_fmin_partial=False,
        is_fmax_partial=False,
        locgroup=0,
        rank=0,
    )

    # ── feature B: the sparse case (no props, no relations) ──────────────
    features["gene_b"] = _feature(organism, t_gene, "GENE_B", None)

    # ── feature C: located, but with NO overlapping neighbour ────────────
    # This exists to exercise the overlap inner-join returning EMPTY.
    # Without it, GENE_A is the only feature whose outer Featureloc loop runs
    # at all, and it always finds a match -- so a rewrite that made the
    # coordinate bounds too broad (dropping fmin__lte/fmax__gte, or the
    # ~Q(feature__type__name=...) exclusion) could still pass. GENE_C sits far
    # from SNV_1 on the same srcfeature, so the query must run and find nothing.
    gene_c = _feature(organism, t_gene, "GENE_C", "GeneGamma")
    features["gene_c"] = gene_c
    Featureloc.objects.create(
        feature=gene_c,
        srcfeature=chrom,
        fmin=5000,
        fmax=5100,
        is_fmin_partial=False,
        is_fmax_partial=False,
        locgroup=0,
        rank=0,
    )

    return features


def _stable_relationships(raw_relationships, id_to_uniquename):
    """Rewrite '{feature_id} {type_name}' entries as '{uniquename} {type_name}'.

    ``_prepare_relationship`` in the command encodes the related feature's
    raw ``feature_id`` primary key. That PK is not reproducible across test
    runs: Postgres sequences advance even when the transaction that
    allocated them is rolled back, so the same fixture gets different
    feature_ids depending on how many other tests ran first (e.g. a fresh
    run of just this module vs. the full ``machado`` suite). Translating
    the id to the feature's uniquename keeps the snapshot comparison
    meaningful regardless of sequence drift, without changing what is
    actually stored in ``FeatureSearchIndex.relationships`` in the database.
    """
    stable = []
    for entry in raw_relationships:
        fid_str, type_name = entry.split(" ", 1)
        uniquename = id_to_uniquename.get(int(fid_str), fid_str)
        stable.append("{} {}".format(uniquename, type_name))
    return stable


def snapshot_index():
    """Return uniquename -> normalized field dict for every index row.

    Multi-value JSON fields are sorted so the comparison is order-insensitive,
    since only ``autocomplete_text`` has a guaranteed order.
    """
    from machado.models import FeatureSearchIndex

    id_to_uniquename = dict(Feature.objects.values_list("feature_id", "uniquename"))

    snapshot = {}
    for row in FeatureSearchIndex.objects.all():
        snapshot[row.uniquename] = {
            "autocomplete_text": row.autocomplete_text,
            "organism": row.organism,
            "so_term": row.so_term,
            "uniquename": row.uniquename,
            "name": row.name,
            "display": row.display,
            "analyses": sorted(row.analyses),
            "doi": sorted(row.doi),
            "biomaterial": sorted(row.biomaterial),
            "treatment": sorted(row.treatment),
            "orthology": row.orthology,
            "orthologous_group": row.orthologous_group,
            "coexpression": row.coexpression,
            "coexpression_group": row.coexpression_group,
            "relationships": sorted(
                _stable_relationships(row.relationships, id_to_uniquename)
            ),
            "orthologs_coexpression": sorted(row.orthologs_coexpression),
        }
    return snapshot
