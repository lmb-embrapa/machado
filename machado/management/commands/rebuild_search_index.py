# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Rebuild the PostgreSQL full-text search index for features.

Usage:
    python manage.py rebuild_search_index [--batch-size 1000]

This replaces the former Haystack ``rebuild_index`` / ``update_index``
commands.  It populates the ``FeatureSearchIndex`` table with denormalised
data from the Chado schema and builds a tsvector column for full-text
search.
"""

from django.conf import settings
from django.contrib.postgres.search import SearchVector
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from machado.management.commands._base import HistoryCommandMixin
from django.db.models import Q
from tqdm import tqdm

from machado.models import (
    Analysis,
    Analysisfeature,
    Feature,
    FeatureCvterm,
    FeatureDbxref,
    FeatureRelationship,
    Featureloc,
    Featureprop,
    FeatureSearchIndex,
)

VALID_PROGRAMS = ["interproscan", "diamond", "blast"]


class Command(HistoryCommandMixin, BaseCommand):
    help = "Rebuild the PostgreSQL full-text search index for features."

    def add_arguments(self, parser):
        parser.add_argument(
            "--batch-size",
            type=int,
            default=1000,
            help="Number of records to create per bulk insert (default: 1000).",
        )

    def handle(self, *args, **options):
        verbosity = options.get("verbosity", 1)
        batch_size = int(options.get("batch_size", 1000))

        try:
            valid_types = settings.MACHADO_VALID_TYPES
        except AttributeError:
            self.stderr.write(
                "Critical error: MACHADO_VALID_TYPES is not defined in settings. Operation aborted."
            )
            return

        overlapping_features = getattr(
            settings,
            "MACHADO_OVERLAPPING_FEATURES",
            ["SNV", "QTL", "copy_number_variation"],
        )

        # ── Pre-compute shared lookups ───────────────────────────────────
        has_overlapping = Feature.objects.filter(
            type__name__in=overlapping_features
        ).exists()

        valid_programs = list(
            Analysis.objects.filter(program__in=VALID_PROGRAMS)
            .distinct("program")
            .values_list("program")
        )

        # ── Get feature queryset (same filter as old index_queryset) ─────
        feature_qs = (
            Feature.objects.filter(
                type__name__in=valid_types, type__cv__name="sequence", is_obsolete=False
            )
            .select_related("organism", "type")
            .order_by("feature_id")
        )

        total = feature_qs.count()
        self.stdout.write(f"Indexing {total} features...")

        # ── Clear existing index ─────────────────────────────────────────
        deleted, _ = FeatureSearchIndex.objects.all().delete()
        if deleted:
            self.stdout.write(f"  Cleared {deleted} stale index entries.")

        # ── Batch-build index entries ────────────────────────────────────
        batch = []
        iterator = tqdm(
            feature_qs.iterator(chunk_size=batch_size),
            total=total,
            disable=verbosity == 0,
            desc="Building index",
        )

        for obj in iterator:
            entry = self._build_entry(
                obj, valid_programs, has_overlapping, valid_types, overlapping_features
            )
            batch.append(entry)

            if len(batch) >= batch_size:
                FeatureSearchIndex.objects.bulk_create(batch, batch_size=batch_size)
                batch = []

        # flush remaining
        if batch:
            FeatureSearchIndex.objects.bulk_create(batch, batch_size=batch_size)

        # ── Update the tsvector column ───────────────────────────────────
        self.stdout.write("  Updating search vectors...")
        FeatureSearchIndex.objects.update(
            search_vector=SearchVector("autocomplete_text", config="english")
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Search index rebuild completed. Indexed {} features.".format(total)
            )
        )

    # ── Field preparation (ported from old search_indexes.py) ────────────

    def _build_entry(
        self, obj, valid_programs, has_overlapping, valid_types, overlapping_features
    ):
        """Build a FeatureSearchIndex instance for a single Feature."""
        organism = self._prepare_organism(obj)
        text = self._prepare_text(
            obj, has_overlapping, valid_types, overlapping_features
        )
        autocomplete = "{} {}".format(organism, text)

        return FeatureSearchIndex(
            feature=obj,
            autocomplete_text=autocomplete,
            organism=organism,
            so_term=obj.type.name,
            uniquename=obj.uniquename,
            name=obj.name,
            display=obj.get_display(),
            analyses=self._prepare_analyses(obj, valid_programs),
            doi=self._prepare_doi(obj),
            biomaterial=self._prepare_biomaterial(obj),
            treatment=self._prepare_treatment(obj),
            orthology=bool(obj.get_orthologous_group()),
            orthologous_group=obj.get_orthologous_group(),
            coexpression=bool(obj.get_coexpression_group()),
            coexpression_group=obj.get_coexpression_group(),
            relationships=self._prepare_relationship(obj),
            orthologs_coexpression=self._prepare_orthologs_coexpression(obj),
        )

    @staticmethod
    def _prepare_organism(obj):
        """Build organism display string."""
        organism = "{} {}".format(obj.organism.genus, obj.organism.species)
        if obj.organism.infraspecific_name:
            organism += " {}".format(obj.organism.infraspecific_name)
        return organism

    @staticmethod
    def _prepare_text(obj, has_overlapping, valid_types, overlapping_features):
        """Aggregate all searchable text."""
        keywords = set()

        if obj.get_display():
            keywords.add(obj.get_display())

        for fdbx in FeatureDbxref.objects.filter(feature=obj):
            keywords.add(fdbx.dbxref.accession)

        for fcv in FeatureCvterm.objects.filter(feature=obj):
            term = "{}:{}".format(
                fcv.cvterm.dbxref.db.name, fcv.cvterm.dbxref.accession
            )
            keywords.add(term)
            keywords.add(fcv.cvterm.name)

        for fr in FeatureRelationship.objects.filter(
            object=obj,
            subject__type__name="protein_match",
            subject__type__cv__name="sequence",
        ):
            keywords.add(fr.subject.uniquename)
            if fr.subject.name is not None:
                keywords.add(fr.subject.name)

        for annotation in obj.get_annotation():
            keywords.add(annotation)

        for doi in obj.get_doi():
            keywords.add(doi)

        for sample in obj.get_expression_samples():
            keywords.add(sample.get("assay_name"))
            keywords.add(sample.get("biomaterial_name"))
            for i in sample.get("biomaterial_description", "").split(" "):
                keywords.add(i)
            for i in sample.get("treatment_name", "").split(" "):
                keywords.add(i)

        if has_overlapping:
            try:
                for location in obj.Featureloc_feature_Feature.filter(
                    feature__type__name__in=valid_types
                ):
                    for overlapping in Featureloc.objects.filter(
                        ~Q(feature__type__name=location.feature.type.name),
                        srcfeature=location.srcfeature,
                        feature__type__name__in=overlapping_features,
                        fmin__lte=location.fmax,
                        fmax__gte=location.fmin,
                    ):
                        keywords.add(overlapping.feature.uniquename)
                        if overlapping.feature.name:
                            keywords.add(overlapping.feature.name)
            except AttributeError:
                pass

        if obj.name is not None:
            keywords.add(obj.name)
        keywords.add(obj.uniquename)
        keywords.discard(None)

        return " ".join(keywords)

    @staticmethod
    def _prepare_analyses(obj, valid_programs):
        """Collect analysis program names."""
        match_part_ids = (
            Featureloc.objects.filter(srcfeature=obj)
            .filter(feature__organism_id=obj.organism_id)
            .filter(feature__type__name="match_part")
            .filter(feature__type__cv__name="sequence")
            .values_list("feature_id")
        )
        match_part_programs = (
            Analysisfeature.objects.filter(feature_id__in=match_part_ids)
            .values_list("analysis__program")
            .distinct()
        )
        result = []
        for i in list(valid_programs):
            if i in list(match_part_programs):
                result.append("{} matches".format(i[0]))
            else:
                result.append("no {} matches".format(i[0]))
        return result

    @staticmethod
    def _prepare_doi(obj):
        """Prepare DOI list."""
        return [doi for doi in obj.get_doi()]

    @staticmethod
    def _prepare_biomaterial(obj):
        """Prepare biomaterial list."""
        result = []
        for sample in obj.get_expression_samples():
            desc = sample.get("biomaterial_description")
            if desc and desc not in result:
                result.append(desc)
        return result

    @staticmethod
    def _prepare_treatment(obj):
        """Prepare treatment list."""
        result = []
        for sample in obj.get_expression_samples():
            name = sample.get("treatment_name")
            if name and name not in result:
                result.append(name)
        return result

    @staticmethod
    def _prepare_relationship(obj):
        """Prepare relationship list as 'feature_id type_name' strings."""
        result = []
        for r in obj.get_relationship():
            result.append("{} {}".format(r.feature_id, r.type.name))
        return result

    @staticmethod
    def _prepare_orthologs_coexpression(obj):
        """Prepare orthologs coexpression."""
        try:
            ortholog_group = Featureprop.objects.get(
                type__cv__name="feature_property",
                type__name="orthologous group",
                feature=obj,
            ).value
        except ObjectDoesNotExist:
            return []

        protein_ids = Featureprop.objects.filter(
            type__cv__name="feature_property",
            type__name="orthologous group",
            value=ortholog_group,
        ).values_list("feature_id", flat=True)

        result = []
        for mrna_protein_obj in FeatureRelationship.objects.filter(
            type__name="translation_of", object_id__in=protein_ids
        ):
            have_coexp = Featureprop.objects.filter(
                type__cv__name="feature_property",
                type__name="coexpression group",
                feature=mrna_protein_obj.subject,
            ).exists()
            if have_coexp:
                result.append(True)
            else:
                result.append(False)
        return result
