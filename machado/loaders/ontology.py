# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Ontology."""
import re
from multiprocessing.synchronize import Lock
from typing import Any, Dict, Optional

from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError

from machado.loaders.exceptions import ImportingError
from machado.models import Cv, Cvterm, Cvtermprop, CvtermDbxref, Cvtermsynonym
from machado.models import CvtermRelationship
from machado.models import Db, Dbxref


class OntologyLoader(object):
    """Ontology."""

    def __init__(self, cv_name: str, cv_definition: str = None) -> None:
        """Invoke all validations."""
        # Save the name and definition to the Cv model
        try:
            # Check if the so file is already loaded
            cv = Cv.objects.get(name=cv_name)

            if cv is not None:
                raise ImportingError(
                    "Cv -> cannot load {} (already registered)".format(cv_name)
                )

        except ObjectDoesNotExist:
            self.cv = Cv.objects.create(name=cv_name, definition=cv_definition)
            self.cv.save()

        # Creating db _global
        self.db_global, created = Db.objects.get_or_create(name="_global")
        # Creating db internal
        self.db_internal, created = Db.objects.get_or_create(name="internal")
        # Creating db OBO_REL
        self.db_obo_rel, created = Db.objects.get_or_create(name="OBO_REL")

        # Creating cv cvterm_property_type
        self.cv_cvterm_property_type, created = Cv.objects.get_or_create(
            name="cvterm_property_type"
        )
        # Creating cv relationship
        self.cv_relationship, created = Cv.objects.get_or_create(name="relationship")
        # Creating cv relationship
        self.cv_synonym_type, created = Cv.objects.get_or_create(name="synonym_type")

        # Creating dbxref and cvterm is_symmetric
        self.dbxref_is_symmetric, created = Dbxref.objects.get_or_create(
            db=self.db_internal, accession="is_symmetric"
        )
        self.cvterm_is_symmetric, created = Cvterm.objects.get_or_create(
            cv=self.cv_cvterm_property_type,
            name="is_symmetric",
            definition="",
            dbxref=self.dbxref_is_symmetric,
            is_obsolete=0,
            is_relationshiptype=0,
        )

        # Creating dbxref and cvterm is_transitive
        dbxref_is_transitive, created = Dbxref.objects.get_or_create(
            db=self.db_internal, accession="is_transitive"
        )
        self.cvterm_is_transitive, created = Cvterm.objects.get_or_create(
            cv=self.cv_cvterm_property_type,
            name="is_transitive",
            definition="",
            dbxref=dbxref_is_transitive,
            is_obsolete=0,
            is_relationshiptype=0,
        )

        # Creating dbxref and cvterm is_class_level
        dbxref_is_class_level, created = Dbxref.objects.get_or_create(
            db=self.db_internal, accession="is_class_level"
        )
        self.cvterm_is_class_level, created = Cvterm.objects.get_or_create(
            cv=self.cv_cvterm_property_type,
            name="is_class_level",
            definition="",
            dbxref=dbxref_is_class_level,
            is_obsolete=0,
            is_relationshiptype=0,
        )

        # Creating dbxref and cvterm is_metadata_tag
        dbxref_is_metadata_tag, created = Dbxref.objects.get_or_create(
            db=self.db_internal, accession="is_metadata_tag"
        )
        self.cvterm_is_metadata_tag, created = Cvterm.objects.get_or_create(
            cv=self.cv_cvterm_property_type,
            name="is_metadata_tag",
            definition="",
            dbxref=dbxref_is_metadata_tag,
            is_obsolete=0,
            is_relationshiptype=0,
        )

        # Creating dbxref and cvterm comment
        dbxref_comment, created = Dbxref.objects.get_or_create(
            db=self.db_internal, accession="comment"
        )
        self.cvterm_comment, created = Cvterm.objects.get_or_create(
            cv=self.cv_cvterm_property_type,
            name="comment",
            definition="",
            dbxref=dbxref_comment,
            is_obsolete=0,
            is_relationshiptype=0,
        )

        # Creating dbxref and cvterm is_a
        dbxref_is_a, created = Dbxref.objects.get_or_create(
            db=self.db_obo_rel, accession="is_a"
        )
        self.cvterm_is_a, created = Cvterm.objects.get_or_create(
            cv=self.cv_relationship,
            name="is_a",
            definition="",
            dbxref=dbxref_is_a,
            is_obsolete=0,
            is_relationshiptype=1,
        )

    def store_type_def(self, typedef: Dict[str, str]) -> None:
        """Store the type_def."""
        # Try to retrieve db from id
        if ":" in typedef["id"]:
            aux_db, typedef_accession = typedef["id"].split(":")
            typedef_db, created = Db.objects.get_or_create(name=aux_db.upper())
            typedef_name = typedef["name"]
        else:
            typedef_db = self.db_global
            typedef_accession = typedef["id"]
            typedef_name = typedef["id"]

        # Save the typedef to the Dbxref model
        dbxref_typedef, created = Dbxref.objects.get_or_create(
            db=typedef_db,
            accession=typedef_accession,
            defaults={"description": typedef.get("def"), "version": ""},
        )

        # Save the typedef to the Cvterm model
        cvterm_typedef, created = Cvterm.objects.get_or_create(
            name=typedef_name,
            is_obsolete=0,
            dbxref=dbxref_typedef,
            defaults={
                "definition": typedef.get("def"),
                "is_relationshiptype": 1,
                "cv": self.cv,
            },
        )

        # Load comment
        if typedef.get("comment") is not None:
            for comment in typedef["comment"]:
                Cvtermprop.objects.get_or_create(
                    cvterm=cvterm_typedef,
                    type_id=self.cvterm_comment.cvterm_id,
                    value=comment,
                    rank=0,
                )

        # Load is_class_level
        if typedef.get("is_class_level") is not None:
            Cvtermprop.objects.get_or_create(
                cvterm=cvterm_typedef,
                type_id=self.cvterm_is_class_level.cvterm_id,
                value=1,
                rank=0,
            )

        # Load is_metadata_tag
        if typedef.get("is_metadata_tag") is not None:
            Cvtermprop.objects.get_or_create(
                cvterm=cvterm_typedef,
                type_id=self.cvterm_is_metadata_tag.cvterm_id,
                value=1,
                rank=0,
            )

        # Load is_symmetric
        if typedef.get("is_symmetric") is not None:
            Cvtermprop.objects.get_or_create(
                cvterm=cvterm_typedef,
                type_id=self.cvterm_is_symmetric.cvterm_id,
                value=1,
                rank=0,
            )

        # Load is_transitive
        if typedef.get("is_transitive") is not None:
            Cvtermprop.objects.get_or_create(
                cvterm=cvterm_typedef,
                type_id=self.cvterm_is_transitive.cvterm_id,
                value=1,
                rank=0,
            )

        if typedef.get("xref") is not None:
            for xref in typedef["xref"]:
                self.process_cvterm_xref(cvterm_typedef, xref)

    def store_term(
        self, n: str, data: Dict[str, Any], lock: Optional[Lock] = None
    ) -> None:
        """Store the ontology terms."""
        # Save the term to the Dbxref model
        aux_db, aux_accession = n.split(":")
        db, created = Db.objects.get_or_create(name=aux_db.upper())
        dbxref, created = Dbxref.objects.get_or_create(db=db, accession=aux_accession)

        # Save the term to the Cvterm model
        if data.get("namespace") is not None:
            cv, created = Cv.objects.get_or_create(name=data["namespace"])
        else:
            cv = self.cv
        try:
            cvterm, created = Cvterm.objects.get_or_create(
                cv=cv,
                name=data["name"],
                definition="",
                dbxref=dbxref,
                is_obsolete=0,
                is_relationshiptype=0,
            )
        except KeyError as e:
            raise ImportingError("{}\nError loading {}".format(e, data))

        # Definitions usually contain recurrent dbxrefs
        # will sometimes break since they're running concurrently with
        # identical values. Locking this function call solved the problem.
        if lock is not None:
            with lock:
                # Load definition and dbxrefs
                if data.get("def"):
                    self.process_cvterm_def(cvterm, data["def"])
        else:
            if data.get("def"):
                self.process_cvterm_def(cvterm, data["def"])

        # Load alt_ids
        if data.get("alt_id") is not None:
            for alt_id in data["alt_id"]:
                aux_db, aux_accession = alt_id.split(":")
                db_alt_id, created = Db.objects.get_or_create(name=aux_db.upper())
                dbxref_alt_id, created = Dbxref.objects.get_or_create(
                    db=db_alt_id, accession=aux_accession
                )
                CvtermDbxref.objects.get_or_create(
                    cvterm=cvterm,
                    dbxref=dbxref_alt_id,
                    defaults={"is_for_definition": 0},
                )

        # Load comment
        if data.get("comment") is not None:
            Cvtermprop.objects.get_or_create(
                cvterm=cvterm,
                type_id=self.cvterm_comment.cvterm_id,
                value=data["comment"],
                rank=0,
            )

        # Load xref
        if data.get("xref") is not None:
            for xref in data["xref"]:
                self.process_cvterm_xref(cvterm, xref)

        # Load synonyms
        if data.get("synonym") is not None:
            for synonym in data["synonym"]:
                self.process_cvterm_so_synonym(cvterm, synonym)

    def store_relationship(self, u: str, v: str, type: str) -> None:
        """Store the relationship between ontology terms."""
        # Get the subject cvterm
        subject_db_name, subject_dbxref_accession = u.split(":")
        subject_db, created = Db.objects.get_or_create(name=subject_db_name.upper())
        subject_dbxref = Dbxref.objects.get(
            db=subject_db, accession=subject_dbxref_accession
        )
        subject_cvterm = Cvterm.objects.get(dbxref=subject_dbxref)

        # Get the object cvterm
        object_db_name, object_dbxref_accession = v.split(":")
        object_db, created = Db.objects.get_or_create(name=object_db_name.upper())
        object_dbxref = Dbxref.objects.get(
            db=object_db, accession=object_dbxref_accession
        )
        object_cvterm = Cvterm.objects.get(dbxref=object_dbxref)

        # Get the relationship type
        if type == "is_a":
            type_cvterm = self.cvterm_is_a
        else:
            type_dbxref = Dbxref.objects.get(db=self.db_global, accession=type)
            type_cvterm = Cvterm.objects.get(dbxref=type_dbxref)

        cvrel = CvtermRelationship.objects.create(
            type_id=type_cvterm.cvterm_id,
            subject_id=subject_cvterm.cvterm_id,
            object_id=object_cvterm.cvterm_id,
        )
        cvrel.save()

    def process_cvterm_def(
        self, cvterm: Cvterm, definition: str, is_for_definition: int = 1
    ) -> None:
        """Process defition to obtain cvterms."""
        text = ""

        """
        Definition format:
        "text" [refdb:refcontent, refdb:refcontent]

        Definition format example:
        "A gene encoding an mRNA that has the stop codon redefined as
         pyrrolysine." [SO:xp]
        """
        # Retrieve text and dbxrefs
        try:
            text, dbxrefs = definition.split('" [')
            text = re.sub(r'^"', "", text)
            dbxrefs = re.sub(r"\]$", "", dbxrefs)
        except ValueError:
            text = definition
            dbxrefs = ""

        if dbxrefs:

            dbxref_list = dbxrefs.split(", ")

            # Save all dbxrefs
            for dbxref in dbxref_list:
                ref_db, ref_content = dbxref.split(":", 1)

                if ref_db == "http":
                    ref_db = "URL"
                    ref_content = "http:" + ref_content

                # Get/Set Dbxref instance: ref_db,ref_content
                db, created = Db.objects.get_or_create(name=ref_db.upper())
                dbxref, created = Dbxref.objects.get_or_create(
                    db=db, accession=ref_content
                )

                # Estabilish the cvterm and the dbxref relationship
                CvtermDbxref.objects.get_or_create(
                    cvterm=cvterm,
                    dbxref=dbxref,
                    defaults={"is_for_definition": is_for_definition},
                )

        cvterm.definition = text
        cvterm.save()

    def process_cvterm_xref(
        self, cvterm: Cvterm, xref: str, is_for_definition: int = 0
    ) -> None:
        """Process cvterm_xref."""
        if xref:

            ref_db, ref_content = xref.split(":", 1)

            if ref_db == "http":
                ref_db = "URL"
                ref_content = "http:" + ref_content

            # Get/Set Dbxref instance: ref_db,ref_content
            db, created = Db.objects.get_or_create(name=ref_db.upper())
            dbxref, created = Dbxref.objects.get_or_create(db=db, accession=ref_content)

            # Estabilish the cvterm and the dbxref relationship
            CvtermDbxref.objects.get_or_create(
                cvterm=cvterm,
                dbxref=dbxref,
                defaults={"is_for_definition": is_for_definition},
            )

    def process_cvterm_go_synonym(
        self, cvterm: Cvterm, synonym: str, synonym_type: str
    ) -> None:
        """Process cvterm_go_synonym.

        Definition format:
        "text" [refdb:refcontent, refdb:refcontent]

        Definition format example:
        "30S ribosomal subunit assembly" [GOC:mah]
        """
        # Retrieve text and dbxrefs
        text, dbxrefs = synonym.split('" [')
        synonym_text = re.sub(r'^"', "", text)
        synonym_type = re.sub(r"_synonym", "", synonym_type).lower()

        # Handling the synonym_type
        db_type, created = Db.objects.get_or_create(name="internal")
        dbxref_type, created = Dbxref.objects.get_or_create(
            db=db_type, accession=synonym_type
        )

        cv_synonym_type, created = Cv.objects.get_or_create(name="synonym_type")
        cvterm_type, created = Cvterm.objects.get_or_create(
            cv=cv_synonym_type,
            name=synonym_type,
            definition="",
            dbxref=dbxref_type,
            is_obsolete=0,
            is_relationshiptype=0,
        )

        # Storing the synonym
        try:
            cvtermsynonym = Cvtermsynonym.objects.create(
                cvterm=cvterm, synonym=synonym_text, type_id=cvterm_type.cvterm_id
            )
            cvtermsynonym.save()
        # Ignore if already created
        except IntegrityError:
            pass

    def process_cvterm_so_synonym(self, cvterm: Cvterm, synonym: str):
        """Process cvterm_so_synonym.

        Definition format:
        "text" cvterm []

        Definition format example:
        "stop codon gained" EXACT []

        Attention:
        There are several cases that don't follow this format.
        Those are being ignored for now.
        """
        pattern = re.compile(r'^"(.+)" (\w+) \[\]$')
        matches = pattern.findall(synonym)

        if len(matches) != 1 or len(matches[0]) != 2:
            return

        synonym_text, synonym_type = matches[0]

        # Handling the synonym_type
        dbxref_type, created = Dbxref.objects.get_or_create(
            db=self.db_internal, accession=synonym_type.lower()
        )
        cvterm_type, created = Cvterm.objects.get_or_create(
            cv=self.cv_synonym_type,
            name=synonym_type.lower(),
            definition="",
            dbxref=dbxref_type,
            is_obsolete=0,
            is_relationshiptype=0,
        )

        # Storing the synonym
        cvtermsynonym = Cvtermsynonym.objects.create(
            cvterm=cvterm, synonym=synonym_text, type_id=cvterm_type.cvterm_id
        )
        cvtermsynonym.save()
