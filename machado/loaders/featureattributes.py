# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Load feature attributes."""

from typing import Dict, Set
from urllib.parse import unquote

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Max

from machado.loaders.exceptions import ImportingError
from machado.models import Cv, Db, Cvterm, Dbxref
from machado.models import FeatureCvterm, FeatureDbxref, FeaturePub
from machado.models import Featureprop, FeaturepropPub, FeatureSynonym
from machado.models import Pub, PubDbxref, Synonym


# The following attributes are handled in a specific manner and should not
# be included in VALID_GFF_ATTRS: id, name, and parent
VALID_GENOME_ATTRS = [
    "dbxref",
    "note",
    "display",
    "alias",
    "ontology_term",
    "orf_classification",
    "synonym",
    "is_circular",
    "gene_synonym",
    "description",
    "product",
    "pacid",
    "doi",
    "freq",
    "cnv_type",
    "annotation",
]

VALID_POLYMORPHISM_ATTRS = ["tsa", "vc"]

VALID_QTL_ATTRS = [
    "qtl_id",
    "qtl_type",
    "abbrev",
    "trait",
    "breed",
    "flankmarker",
    "map_type",
    "model",
    "peak_cm",
    "test_base",
    "significance",
    "p-value",
    "trait_id",
    "pubmed_id",
    "doi",
]


class FeatureAttributesLoader(object):
    """Load feature attributes."""

    help = "Load feature attributes."

    def __init__(self, filecontent: str, doi: str = None) -> None:
        """Execute the init function."""
        # initialization of lists/sets to store ignored attributes, and
        # ignored goterms
        self.db_null, created = Db.objects.get_or_create(name="null")
        null_dbxref, created = Dbxref.objects.get_or_create(
            db=self.db_null, accession="null"
        )
        null_cv, created = Cv.objects.get_or_create(name="null")
        null_cvterm, created = Cvterm.objects.get_or_create(
            cv=null_cv,
            name="null",
            definition="",
            dbxref=null_dbxref,
            is_obsolete=0,
            is_relationshiptype=0,
        )

        if filecontent == "genome":
            self.filter = VALID_GENOME_ATTRS
        elif filecontent == "polymorphism":
            self.filter = VALID_POLYMORPHISM_ATTRS
        elif filecontent == "qtl":
            self.filter = VALID_QTL_ATTRS
        else:
            raise ImportingError(
                "Attributes type required: (eg. genome, polymorphism, qtl)"
            )

        # Retrieve DOI's Dbxref
        dbxref_doi = None
        pub_dbxref_doi = None
        if doi:
            try:
                dbxref_doi = Dbxref.objects.get(accession=doi)
            except ObjectDoesNotExist:
                raise ImportingError("{} not registered.".format(doi))
            try:
                pub_dbxref_doi = PubDbxref.objects.get(dbxref=dbxref_doi)
            except ObjectDoesNotExist:
                raise ImportingError("{} not registered.".format(doi))
            try:
                self.pub = Pub.objects.get(pub_id=pub_dbxref_doi.pub_id)
            except ObjectDoesNotExist:
                raise ImportingError("{} not registered.".format(doi))
        else:
            self.pub, created = Pub.objects.get_or_create(
                miniref="null",
                uniquename="null",
                type_id=null_cvterm.cvterm_id,
                is_obsolete=False,
            )

        self.ignored_attrs: Set[str] = set()
        self.ignored_goterms: Set[str] = set()

    def get_attributes(self, attributes: str) -> Dict[str, str]:
        """Get attributes."""
        result = dict()
        fields = attributes.split(";")
        for field in fields:
            try:
                key, value = field.split("=")

                if key.lower() not in self.filter and key.lower() not in [
                    "id",
                    "name",
                    "parent",
                ]:
                    self.ignored_attrs.add(key)
                else:
                    key = key.lower().replace("qtl_id", "id")
                    result[key] = unquote(value)
            except ValueError:
                pass

        return result

    def process_attributes(self, feature_id: int, attrs: Dict[str, str]) -> None:
        """Process the valid attributes."""
        try:
            cvterm_exact = Cvterm.objects.get(name="exact", cv__name="synonym_type")
        except ObjectDoesNotExist as e:
            raise ImportingError(e)

        # Don't forget to add the attribute to the constant VALID_GENOME_ATTRS
        for key in attrs:
            if key not in self.filter:
                continue
            elif key in ["ontology_term"]:
                # store in featurecvterm
                terms = attrs[key].split(",")
                for term in terms:
                    try:
                        aux_db, aux_term = term.split(":", 1)
                        term_db = Db.objects.get(name=aux_db.upper())
                        dbxref = Dbxref.objects.get(db=term_db, accession=aux_term)
                        cvterm = Cvterm.objects.get(dbxref=dbxref)
                        FeatureCvterm.objects.create(
                            feature_id=feature_id,
                            cvterm=cvterm,
                            pub=self.pub,
                            is_not=False,
                            rank=0,
                        )
                    except ObjectDoesNotExist:
                        self.ignored_goterms.add(term)
            elif key in ["dbxref"]:
                try:
                    dbxrefs = attrs[key].split(",")
                except ValueError as e:
                    raise ImportingError("{}: {}".format(attrs[key], e))
                for dbxref in dbxrefs:
                    # It expects just one dbxref formated as XX:012345
                    try:
                        aux_db, aux_dbxref = dbxref.split(":", 1)
                    except ValueError as e:
                        raise ImportingError("{}: {}".format(dbxref, e))
                    db, created = Db.objects.get_or_create(name=aux_db.upper())
                    dbxref, created = Dbxref.objects.get_or_create(
                        db=db, accession=aux_dbxref
                    )
                    FeatureDbxref.objects.create(
                        feature_id=feature_id, dbxref=dbxref, is_current=1
                    )
            elif key in ["pacid"]:
                db, created = Db.objects.get_or_create(name="PACID")
                dbxref, created = Dbxref.objects.get_or_create(
                    db=db, accession=attrs[key]
                )
                FeatureDbxref.objects.create(
                    feature_id=feature_id, dbxref=dbxref, is_current=1
                )
            elif key in ["doi"]:
                try:
                    doi_obj = Dbxref.objects.get(
                        accession=attrs[key].lower(), db__name="DOI"
                    )
                    pub_obj = Pub.objects.get(PubDbxref_pub_Pub__dbxref=doi_obj)
                except ObjectDoesNotExist:
                    raise ImportingError("{} not registered.".format(attrs[key]))

                FeaturePub.objects.get_or_create(feature_id=feature_id, pub=pub_obj)

            elif key in ["alias", "gene_synonym", "synonym", "abbrev"]:
                synonym, created = Synonym.objects.get_or_create(
                    name=attrs.get(key),
                    defaults={
                        "type_id": cvterm_exact.cvterm_id,
                        "synonym_sgml": attrs.get(key),
                    },
                )
                FeatureSynonym.objects.create(
                    synonym=synonym,
                    feature_id=feature_id,
                    pub=self.pub,
                    is_current=True,
                    is_internal=False,
                )
            elif key in ["annotation"]:
                annotation_dbxref, created = Dbxref.objects.get_or_create(
                    db=self.db_null, accession=key
                )
                cv_feature_property, created = Cv.objects.get_or_create(
                    name="feature_property"
                )
                annotation_cvterm, created = Cvterm.objects.get_or_create(
                    cv=cv_feature_property,
                    name=key,
                    dbxref=annotation_dbxref,
                    defaults={
                        "definition": "",
                        "is_relationshiptype": 0,
                        "is_obsolete": 0,
                    },
                )
                try:
                    featureprop_obj = Featureprop.objects.get(
                        feature_id=feature_id,
                        type_id=annotation_cvterm.cvterm_id,
                        value=attrs.get(key),
                    )
                    featureprop_obj.value = attrs.get(key)
                    featureprop_obj.save()
                except ObjectDoesNotExist:
                    feature_props = Featureprop.objects.filter(
                        feature_id=feature_id,
                        type_id=annotation_cvterm.cvterm_id,
                    )
                    max_rank = feature_props.aggregate(Max("rank")).get("rank__max")
                    if max_rank is None:
                        max_rank = 0
                    else:
                        max_rank += 1
                    featureprop_obj, created = Featureprop.objects.get_or_create(
                        feature_id=feature_id,
                        type_id=annotation_cvterm.cvterm_id,
                        value=attrs.get(key),
                        rank=max_rank,
                    )
                if self.pub.uniquename != "null":
                    FeaturepropPub.objects.get_or_create(
                        featureprop=featureprop_obj, pub=self.pub
                    )
                    FeaturePub.objects.get_or_create(
                        feature_id=feature_id, pub=self.pub
                    )
            else:
                note_dbxref, created = Dbxref.objects.get_or_create(
                    db=self.db_null, accession=key
                )
                cv_feature_property, created = Cv.objects.get_or_create(
                    name="feature_property"
                )
                note_cvterm, created = Cvterm.objects.get_or_create(
                    cv=cv_feature_property,
                    name=key,
                    dbxref=note_dbxref,
                    defaults={
                        "definition": "",
                        "is_relationshiptype": 0,
                        "is_obsolete": 0,
                    },
                )
                featureprop_obj, created = Featureprop.objects.get_or_create(
                    feature_id=feature_id,
                    type_id=note_cvterm.cvterm_id,
                    rank=0,
                    defaults={"value": attrs.get(key)},
                )
                if self.pub.uniquename != "null":
                    FeaturepropPub.objects.get_or_create(
                        featureprop=featureprop_obj, pub=self.pub
                    )
                if not created:
                    featureprop_obj.value = attrs.get(key)
                    featureprop_obj.save()
