# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Create database from chado default_schema.sql."""
from django.apps import apps
from django.db import migrations

EVIDENCE_CODES = {
    "EXP": "Inferred from Experiment",
    "IDA": "Inferred from Direct Assay",
    "IPI": "Inferred from Physical Interaction",
    "IMP": "Inferred from Mutant Phenotype",
    "IGI": "Inferred from Genetic Interaction",
    "IEP": "Inferred from Expression Pattern",
    "HTP": "Inferred from High Throughput Experiment",
    "HDA": "Inferred from High Throughput Direct Assay",
    "HMP": "Inferred from High Throughput Mutant Phenotype",
    "HGI": "Inferred from High Throughput Genetic Interaction",
    "HEP": "Inferred from High Throughput Expression Pattern",
    "ISS": "Inferred from Sequence or structural Similarity",
    "ISO": "Inferred from Sequence Orthology",
    "ISA": "Inferred from Sequence Alignment",
    "ISM": "Inferred from Sequence Model",
    "IGC": "Inferred from Genomic Context",
    "IBA": "Inferred from Biological aspect of Ancestor",
    "IBD": "Inferred from Biological aspect of Descendant",
    "IKR": "Inferred from Key Residues",
    "IRD": "Inferred from Rapid Divergence",
    "RCA": "Inferred from Reviewed Computational Analysis",
    "TAS": "Traceable Author Statement",
    "NAS": "Non-traceable Author Statement",
    "IC": "Inferred by Curator",
    "ND": "No biological Data available",
    "IEA": "Inferred from Electronic Annotation",
    "NR": "Not recorded",
}


def populate_evidence_codes(migrate_apps, schema_editor):
    """Populate DB, Dbxref, Cv and Cvterm with GO evidence codes."""
    Db = apps.get_model("machado", "Db")
    Dbxref = apps.get_model("machado", "Dbxref")
    Cv = apps.get_model("machado", "cv")
    Cvterm = apps.get_model("machado", "cvterm")

    db_obj, created = Db.objects.get_or_create(
        name="evidence_code",
        description="GO evidence_codes",
        url="geneontology.org/docs/guide-go-evidence-codes",
    )
    cv_obj, created = Cv.objects.get_or_create(
        name="evidence_code", definition="GO evidence codes"
    )

    for key, value in EVIDENCE_CODES.items():
        dbxref_obj, created = Dbxref.objects.get_or_create(db=db_obj, accession=key)
        Cvterm.objects.get_or_create(
            cv=cv_obj,
            name=key,
            definition=value,
            dbxref=dbxref_obj,
            is_obsolete=0,
            is_relationshiptype=0,
        )


class Migration(migrations.Migration):
    """Migration."""

    dependencies = [
        ("machado", "0001_initial"),
        ("machado", "0002_add_index"),
        ("machado", "0003_add_multispecies"),
    ]

    operations = [migrations.RunPython(populate_evidence_codes)]
