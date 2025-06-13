# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Load feature file."""

from datetime import datetime, timezone
from time import time
from typing import Dict, List, Union, Set

from Bio.SearchIO._model import Hit
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db.utils import IntegrityError
from pysam.libctabixproxies import GTFProxy, VCFProxy

from machado.loaders.common import retrieve_feature_id, retrieve_cvterm
from machado.loaders.exceptions import ImportingError
from machado.loaders.featureattributes import FeatureAttributesLoader
from machado.models import Cv, Db, Cvterm, Dbxref, Dbxrefprop, Organism
from machado.models import Feature, FeatureCvterm, FeatureDbxref, Featureloc
from machado.models import FeatureRelationship, FeatureRelationshipprop
from machado.models import Featureprop, FeaturePub, Pub, PubDbxref


class FeatureLoaderBase(object):
    """Shared base for loading feature records."""

    def __init__(self, source: str, filename: str, doi: str = None) -> None:
        """Execute the init function."""
        # initialization of lists/sets to store ignored attributes,
        # ignored goterms, and relationships
        self.cache: Dict[str, str] = dict()
        self.usedcache = 0
        self.relationships: List[Dict[str, str]] = list()
        self.ignored_attrs: Set[str] = set()
        self.ignored_goterms: Set[str] = set()

        try:
            self.db, created = Db.objects.get_or_create(name=source.upper())
            self.filename = filename
        except IntegrityError as e:
            raise ImportingError(e)

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
        self.pub, created = Pub.objects.get_or_create(
            miniref="null",
            uniquename="null",
            type_id=null_cvterm.cvterm_id,
            is_obsolete=False,
        )

        self.cvterm_contained_in = Cvterm.objects.get(
            name="located in", cv__name="relationship"
        )
        self.aa_cvterm = Cvterm.objects.get(name="polypeptide", cv__name="sequence")
        self.so_term_protein_match = Cvterm.objects.get(
            name="protein_match", cv__name="sequence"
        )
        # Retrieve DOI's Dbxref
        dbxref_doi = None
        self.pub_dbxref_doi = None
        if doi:
            try:
                dbxref_doi = Dbxref.objects.get(accession=doi)
            except ObjectDoesNotExist:
                raise ImportingError("{} not registered.".format(doi))
            try:
                self.pub_dbxref_doi = PubDbxref.objects.get(dbxref=dbxref_doi)
            except ObjectDoesNotExist:
                raise ImportingError("{} not registered.".format(doi))


class FeatureLoader(FeatureLoaderBase):
    """Load single-organism feature records."""

    help = "Load single-organism feature records."

    def __init__(
        self, source: str, filename: str, organism: Organism, doi: str = None
    ) -> None:
        """Execute the init function."""

        if organism is not None:
            self.organism = organism
        else:
            raise ImportingError("FeatureLoader requires an organism parameter")

        super(FeatureLoader, self).__init__(source, filename, doi)

    def store_tabix_GFF_feature(self, tabix_feature: GTFProxy, qtl: bool) -> None:
        """Store tabix feature."""

        filecontent = "qtl" if qtl else "genome"

        attrs_loader = FeatureAttributesLoader(filecontent=filecontent)
        attrs_dict = attrs_loader.get_attributes(tabix_feature.attributes)
        self.ignored_attrs = attrs_loader.ignored_attrs
        self.ignored_goterms = attrs_loader.ignored_goterms

        if qtl:
            cvterm = Cvterm.objects.get(name="QTL", cv__name="sequence")
            attrs_dict["qtl_type"] = tabix_feature.feature
        else:
            try:
                cvterm = Cvterm.objects.get(
                    name=tabix_feature.feature, cv__name="sequence"
                )
            except ObjectDoesNotExist:
                raise ImportingError(
                    "{} is not a sequence ontology term.".format(tabix_feature.feature)
                )

        attrs_id = attrs_dict.get("id")
        attrs_name = attrs_dict.get("name")
        try:
            attrs_parent = attrs_dict.get("parent").split(",")
        except AttributeError:
            attrs_parent = list()

        # set id = auto# for features that lack it
        if attrs_id is None:
            attrs_id = "auto{}".format(str(time()))

        try:
            dbxref, created = Dbxref.objects.get_or_create(
                db=self.db, accession=attrs_id, version=self.filename
            )
            Dbxrefprop.objects.get_or_create(
                dbxref=dbxref,
                type_id=self.cvterm_contained_in.cvterm_id,
                value=self.filename,
                rank=0,
            )
            feature_id = Feature.objects.create(
                organism=self.organism,
                uniquename=attrs_id,
                type_id=cvterm.cvterm_id,
                name=attrs_name,
                dbxref=dbxref,
                is_analysis=False,
                is_obsolete=False,
                timeaccessioned=datetime.now(timezone.utc),
                timelastmodified=datetime.now(timezone.utc),
            ).feature_id
        except IntegrityError as e:
            raise ImportingError("ID {} already registered. {}".format(attrs_id, e))

        # DOI: try to link feature to publication's DOI
        if feature_id and self.pub_dbxref_doi:
            try:
                FeaturePub.objects.get_or_create(
                    feature_id=feature_id, pub_id=self.pub_dbxref_doi.pub_id
                )
            except IntegrityError as e:
                raise ImportingError(e)

        srcdb = Db.objects.get(name="FASTA_SOURCE")
        try:
            srcdbxref = Dbxref.objects.get(accession=tabix_feature.contig, db=srcdb)
        except ObjectDoesNotExist as e:
            raise ImportingError(
                "{} {} ({})".format(srcdb.name, tabix_feature.contig, e)
            )
        srcfeature = Feature.objects.filter(
            dbxref=srcdbxref, organism=self.organism
        ).values_list("feature_id", flat=True)
        if len(srcfeature) == 1:
            srcfeature_id = srcfeature.first()
        else:
            raise ImportingError(
                "Parent not found: {}. It's required to load "
                "a reference FASTA file before loading features.".format(
                    tabix_feature.contig
                )
            )

        # the database requires -1, 0, and +1 for strand
        if tabix_feature.strand == "+":
            strand = +1
        elif tabix_feature.strand == "-":
            strand = -1
        else:
            strand = 0

        # if row.frame is . phase = None
        # some versions of pysam throws ValueError
        try:
            phase = tabix_feature.frame
            if tabix_feature.frame == ".":
                phase = None
        except ValueError:
            phase = None

        try:
            Featureloc.objects.get_or_create(
                feature_id=feature_id,
                srcfeature_id=srcfeature_id,
                fmin=tabix_feature.start,
                is_fmin_partial=False,
                fmax=tabix_feature.end,
                is_fmax_partial=False,
                strand=strand,
                phase=phase,
                locgroup=0,
                rank=0,
            )
        except IntegrityError as e:
            print(
                attrs_id,
                srcdbxref,
                tabix_feature.start,
                tabix_feature.end,
                strand,
                phase,
            )
            raise ImportingError(e)

        # Process attrs_dict after the creation of the feature
        attrs_loader.process_attributes(feature_id, attrs_dict)

        for parent in attrs_parent:
            self.relationships.append({"object_id": attrs_id, "subject_id": parent})

        # Additional protein record for each transcript with the exact same ID
        transcripts_types = ["mRNA", "C_gene_segment", "V_gene_segment"]
        if tabix_feature.feature in transcripts_types:
            translation_of = Cvterm.objects.get(
                name="translation_of", cv__name="sequence"
            )
            feature_mRNA_translation_id = Feature.objects.create(
                organism=self.organism,
                uniquename=attrs_id,
                type_id=self.aa_cvterm.cvterm_id,
                name=attrs_name,
                dbxref=dbxref,
                is_analysis=False,
                is_obsolete=False,
                timeaccessioned=datetime.now(timezone.utc),
                timelastmodified=datetime.now(timezone.utc),
            ).feature_id
            FeatureRelationship.objects.create(
                object_id=feature_mRNA_translation_id,
                subject_id=feature_id,
                type=translation_of,
                rank=0,
            )

    def store_relationship(
        self, subject_id: int, object_id: int
    ) -> FeatureRelationship:
        """Retrieve the relationship object."""
        part_of = Cvterm.objects.get(name="part_of", cv__name="sequence")

        try:
            fr = FeatureRelationship(
                subject_id=Feature.objects.exclude(type=self.aa_cvterm)
                .get(uniquename=subject_id, organism=self.organism)
                .feature_id,
                object_id=Feature.objects.exclude(type=self.aa_cvterm)
                .get(uniquename=object_id, organism=self.organism)
                .feature_id,
                type_id=part_of.cvterm_id,
                rank=0,
            )
            fr.save()
        except ObjectDoesNotExist:
            print(
                "Parent/Feature ({}/{}) not registered.".format(object_id, subject_id)
            )

    def store_tabix_VCF_feature(self, tabix_feature: VCFProxy) -> None:
        """Store tabix feature from VCF files."""

        attrs_loader = FeatureAttributesLoader(filecontent="polymorphism")
        attrs_dict = attrs_loader.get_attributes(tabix_feature.info)
        self.ignored_attrs = attrs_loader.ignored_attrs
        self.ignored_goterms = attrs_loader.ignored_goterms

        if attrs_dict.get("vc"):
            attrs_class = attrs_dict.get("vc")
        elif attrs_dict.get("tsa"):
            attrs_class = attrs_dict.get("tsa")
        else:
            raise ImportingError(
                "{}: Impossible to get the attribute which defines the type of variation (eg. TSA, VC)".format(
                    tabix_feature.id
                )
            )

        try:
            cvterm = retrieve_cvterm(cv="sequence", term=attrs_class)
        except ObjectDoesNotExist:
            raise ImportingError(
                "{} is not a sequence ontology term.".format(attrs_class)
            )

        try:
            dbxref, created = Dbxref.objects.get_or_create(
                db=self.db, accession=tabix_feature.id
            )
            Dbxrefprop.objects.get_or_create(
                dbxref=dbxref,
                type_id=self.cvterm_contained_in.cvterm_id,
                rank=0,
            )
            name = "{}->{}".format(tabix_feature.ref, tabix_feature.alt)
            feature_id = Feature.objects.create(
                organism=self.organism,
                uniquename=tabix_feature.id,
                name=name,
                type_id=cvterm.cvterm_id,
                dbxref=dbxref,
                is_analysis=False,
                is_obsolete=False,
                timeaccessioned=datetime.now(timezone.utc),
                timelastmodified=datetime.now(timezone.utc),
            ).feature_id
        except IntegrityError as e:
            raise ImportingError(
                "ID {} already registered. {}".format(tabix_feature.id, e)
            )

        if tabix_feature.qual != ".":
            cvterm_qual = Cvterm.objects.get(name="quality_value", cv__name="sequence")
            featureprop_obj = Featureprop(
                feature_id=feature_id,
                type=cvterm_qual,
                value=tabix_feature.qual,
                rank=0,
            )
            featureprop_obj.save()

        # DOI: try to link feature to publication's DOI
        if feature_id and self.pub_dbxref_doi:
            try:
                FeaturePub.objects.get_or_create(
                    feature_id=feature_id, pub_id=self.pub_dbxref_doi.pub_id
                )
            except IntegrityError as e:
                raise ImportingError(e)

        srcdb = Db.objects.get(name="FASTA_SOURCE")
        try:
            srcdbxref = Dbxref.objects.get(accession=tabix_feature.contig, db=srcdb)
        except ObjectDoesNotExist as e:
            raise ImportingError(
                "{} {} ({})".format(srcdb.name, tabix_feature.contig, e)
            )
        srcfeature = Feature.objects.filter(
            dbxref=srcdbxref, organism=self.organism
        ).values_list("feature_id", flat=True)
        if len(srcfeature) == 1:
            srcfeature_id = srcfeature.first()
        else:
            raise ImportingError(
                "Parent not found: {}. It's required to load "
                "a reference FASTA file before loading features.".format(
                    tabix_feature.contig
                )
            )

        # Reference allele
        try:
            Featureloc.objects.get_or_create(
                feature_id=feature_id,
                srcfeature_id=srcfeature_id,
                fmin=tabix_feature.pos,
                is_fmin_partial=False,
                fmax=tabix_feature.pos + 1,
                is_fmax_partial=False,
                residue_info=tabix_feature.ref,
                locgroup=0,
                rank=0,
            )
        except IntegrityError as e:
            print(tabix_feature.id, srcdbxref, tabix_feature.pos)
            raise ImportingError(e)

        # Alternative alleles
        rank = 1
        for allele in tabix_feature.alt.split(","):
            try:
                Featureloc.objects.get_or_create(
                    feature_id=feature_id,
                    fmin=tabix_feature.pos,
                    is_fmin_partial=False,
                    fmax=tabix_feature.pos + 1,
                    is_fmax_partial=False,
                    residue_info=allele,
                    locgroup=0,
                    rank=rank,
                )
            except IntegrityError as e:
                print(tabix_feature.id, srcdbxref, tabix_feature.pos)
                raise ImportingError(e)
            rank += 1

    def store_feature_annotation(
        self,
        feature: str,
        soterm: str,
        cvterm: str,
        annotation: str,
        doi: Union[str, None],
    ) -> None:
        """Store feature annotation."""
        feature_id = retrieve_feature_id(
            accession=feature, soterm=soterm, organism=self.organism
        )
        attrs_str = "{}={};".format(cvterm, annotation)

        attrs_loader = FeatureAttributesLoader(filecontent="genome", doi=doi)
        attrs_dict = attrs_loader.get_attributes(attrs_str)
        attrs_loader.process_attributes(feature_id, attrs_dict)
        self.ignored_attrs = attrs_loader.ignored_attrs
        self.ignored_goterms = attrs_loader.ignored_goterms

    def store_feature_dbxref(self, feature: str, soterm: str, dbxref: str) -> None:
        """Store feature dbxref."""
        feature_id = retrieve_feature_id(
            accession=feature, soterm=soterm, organism=self.organism
        )

        try:
            db_name, dbxref_accession = dbxref.split(":", 1)
        except ValueError:
            raise ImportingError(
                "Incorrect DBxRef {}. It should have two colon-separated values (eg. DB:DBxREF).".format(
                    dbxref
                )
            )
        db_obj, created = Db.objects.get_or_create(name=db_name)
        dbxref_obj, created = Dbxref.objects.get_or_create(
            db=db_obj, accession=dbxref_accession
        )
        FeatureDbxref.objects.get_or_create(
            feature_id=feature_id, dbxref=dbxref_obj, is_current=True
        )

    def store_feature_publication(self, feature: str, soterm: str, doi: str) -> None:
        """Store feature publication."""
        feature_id = retrieve_feature_id(
            accession=feature, soterm=soterm, organism=self.organism
        )
        try:
            doi_obj = Dbxref.objects.get(accession=doi.lower(), db__name="DOI")
            pub_obj = Pub.objects.get(PubDbxref_pub_Pub__dbxref=doi_obj)
        except ObjectDoesNotExist:
            raise ImportingError("{} not registered.".format(doi))

        FeaturePub.objects.get_or_create(feature_id=feature_id, pub=pub_obj)

    def store_feature_pairs(
        self,
        pair: list,
        term: Union[str, Cvterm],
        soterm: str = "mRNA",
        value: str = None,
        cache: int = 0,
    ) -> None:
        """Store Feature Relationship Pairs."""
        # only cvterm_id allowed
        if isinstance(term, Cvterm):
            cvterm_id = term.cvterm_id
        else:
            cvterm_id = term
        # lets get feature_ids from the pair
        try:
            subject_id = retrieve_feature_id(
                accession=pair[0], soterm=soterm, organism=self.organism
            )
            object_id = retrieve_feature_id(
                accession=pair[1], soterm=soterm, organism=self.organism
            )
            frelationship_id = FeatureRelationship.objects.create(
                subject_id=subject_id,
                object_id=object_id,
                type_id=cvterm_id,
                value=value,
                rank=0,
            ).feature_relationship_id
            FeatureRelationshipprop.objects.create(
                feature_relationship_id=frelationship_id,
                type_id=self.cvterm_contained_in.cvterm_id,
                value=self.filename,
                rank=0,
            )
        except ObjectDoesNotExist:
            print("Feature from pair ({}/{}) not registered.".format(pair[0], pair[1]))
        except IntegrityError as e:
            raise ImportingError(e)

    def store_feature_groups(
        self,
        group: list,
        term: Union[int, Cvterm],
        organism: Union[str, Organism],
        soterm: str = "mRNA",
        value: str = None,
        cache: int = 0,
    ) -> None:
        """Store Feature Relationship Groups."""
        # only cvterm_id allowed
        if isinstance(term, Cvterm):
            cvterm_id = term.cvterm_id
        else:
            cvterm_id = term
        featureprops = list()
        feature_id_list = list()
        for acc in group:
            try:
                # retrieves feature_id from dbxref's accession
                feature_id_list.append(
                    retrieve_feature_id(accession=acc, soterm=soterm, organism=organism)
                )
            except (MultipleObjectsReturned, ObjectDoesNotExist):
                pass

        # only stores clusters with 2 or more members
        if len(feature_id_list) > 1:
            for feature_id in feature_id_list:
                featureprops.append(
                    Featureprop(
                        feature_id=feature_id, type_id=cvterm_id, value=value, rank=0
                    )
                )
            try:
                Featureprop.objects.bulk_create(featureprops)
            except IntegrityError as e:
                raise ImportingError(e)


class MultispeciesFeatureLoader(FeatureLoaderBase):
    """Load multi-organism feature records."""

    help = "Load multi-organism feature records."

    def retrieve_feature_id(self, accession: str, soterm: str) -> int:
        """
        like machado.loaders.common.retreive_feature_id, but assumes acession is unique across all organisms
        """

        """Retrieve feature object."""
        # feature.uniquename
        try:
            return Feature.objects.get(
                uniquename=accession,
                type__cv__name="sequence",
                type__name=soterm,
            ).feature_id
        except (MultipleObjectsReturned, ObjectDoesNotExist):
            pass

        # soterm-feature.uniquename
        try:
            return Feature.objects.get(
                uniquename="{}-{}".format(soterm, accession),
                type__cv__name="sequence",
                type__name=soterm,
            ).feature_id
        except (MultipleObjectsReturned, ObjectDoesNotExist):
            pass

        # feature.name
        try:
            return Feature.objects.get(
                name__iexact=accession,
                type__cv__name="sequence",
                type__name=soterm,
            ).feature_id
        except (MultipleObjectsReturned, ObjectDoesNotExist):
            pass

        # feature.dbxref.accession
        try:
            return Feature.objects.get(
                dbxref__accession__iexact=accession,
                type__cv__name="sequence",
                type__name=soterm,
            ).feature_id
        except (MultipleObjectsReturned, ObjectDoesNotExist):
            pass

        # featuredbxref.dbxref.accession
        try:
            return FeatureDbxref.objects.get(
                dbxref__accession__iexact=accession,
                feature__type__cv__name="sequence",
                feature__type__name=soterm,
            ).feature_id
        except ObjectDoesNotExist:
            raise ObjectDoesNotExist("{} {} does not exist".format(soterm, accession))
        except MultipleObjectsReturned:
            raise MultipleObjectsReturned(
                "{} {} matches multiple features".format(soterm, accession)
            )

    def store_bio_searchio_hit(self, searchio_hit: Hit, target: str) -> None:
        """Store bio searchio hit."""

        organism_obj, created = Organism.objects.get_or_create(
            abbreviation="multispecies",
            genus="multispecies",
            species="multispecies",
            common_name="multispecies",
        )

        if not hasattr(searchio_hit, "accession"):
            searchio_hit.accession = None

        # if interproscan-xml parsing, get db name from Hit.attributes.
        if target == "InterPro":
            db_name = searchio_hit.attributes["Target"].upper()
            # prevents the creation of multiple databases for SIGNALP
            if db_name.startswith("SIGNALP"):
                db_name = "SIGNALP"
            db, created = Db.objects.get_or_create(name=db_name)
        # if blast-xml parsing, db name is self.db ("BLAST_source")
        else:
            db = self.db

        dbxref, created = Dbxref.objects.get_or_create(db=db, accession=searchio_hit.id)
        feature, created = Feature.objects.get_or_create(
            organism=organism_obj,
            uniquename=searchio_hit.id,
            type_id=self.so_term_protein_match.cvterm_id,
            name=searchio_hit.accession,
            dbxref=dbxref,
            defaults={
                "is_analysis": False,
                "is_obsolete": False,
                "timeaccessioned": datetime.now(timezone.utc),
                "timelastmodified": datetime.now(timezone.utc),
            },
        )

        for aux_dbxref in searchio_hit.dbxrefs:
            aux_db, aux_term = aux_dbxref.split(":", 1)
            if aux_db == "GO":
                try:
                    term_db = Db.objects.get(name=aux_db.upper())
                    dbxref = Dbxref.objects.get(db=term_db, accession=aux_term)
                    cvterm = Cvterm.objects.get(dbxref=dbxref)
                    FeatureCvterm.objects.get_or_create(
                        feature=feature,
                        cvterm=cvterm,
                        pub=self.pub,
                        is_not=False,
                        rank=0,
                    )
                except ObjectDoesNotExist:
                    self.ignored_goterms.add(aux_dbxref)
            else:
                term_db, created = Db.objects.get_or_create(name=aux_db.upper())
                dbxref, created = Dbxref.objects.get_or_create(
                    db=term_db, accession=aux_term
                )
                FeatureDbxref.objects.get_or_create(
                    feature=feature, dbxref=dbxref, is_current=1
                )

        return None

    def store_feature_groups(
        self,
        group: list,
        term: Union[int, Cvterm],
        soterm: str = "mRNA",
        value: str = None,
        cache: int = 0,
    ) -> None:
        """Store Feature Relationship Groups."""
        # only cvterm_id allowed
        if isinstance(term, Cvterm):
            cvterm_id = term.cvterm_id
        else:
            cvterm_id = term
        featureprops = list()
        feature_id_list = list()
        for acc in group:
            try:
                # retrieves feature_id from dbxref's accession
                feature_id_list.append(
                    self.retrieve_feature_id(accession=acc, soterm=soterm)
                )
            except (MultipleObjectsReturned, ObjectDoesNotExist):
                pass

        # only stores clusters with 2 or more members
        if len(feature_id_list) > 1:
            for feature_id in feature_id_list:
                featureprops.append(
                    Featureprop(
                        feature_id=feature_id, type_id=cvterm_id, value=value, rank=0
                    )
                )
            try:
                Featureprop.objects.bulk_create(featureprops)
            except IntegrityError as e:
                raise ImportingError(e)
