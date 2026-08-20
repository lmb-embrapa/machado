# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Rebuild the PostgreSQL full-text search index for features.

Usage:
    python manage.py rebuild_search_index [--batch-size 2000]
    python manage.py rebuild_search_index --resume
    python manage.py rebuild_search_index --restart

Populates ``FeatureSearchIndex`` with denormalised data from the Chado
schema. ``search_vector`` is a generated column maintained by PostgreSQL, so
no separate tsvector pass is required.

Related data is fetched in batches (a fixed number of queries per chunk of
features rather than per feature), which is what makes a multi-million-row
rebuild practical.
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from django.db.models import Max
from tqdm import tqdm

from machado.management.commands._base import HistoryCommandMixin
from machado.models import Feature, FeatureSearchIndex
from machado.searchindex import (
    IndexConfig,
    IndexRunCache,
    build_entries,
    prefetch_chunk,
)


class Command(HistoryCommandMixin, BaseCommand):
    """Rebuild the PostgreSQL full-text search index for features."""

    help = "Rebuild the PostgreSQL full-text search index for features."

    #: Set from --verbosity in handle(). Declared here so report() is safe if a
    #: caller instantiates Command() and reaches a helper without handle().
    verbosity = 1

    def add_arguments(self, parser):
        """Define the command arguments."""
        parser.add_argument(
            "--batch-size",
            type=int,
            default=2000,
            help="Features per chunk (default: 2000).",
        )
        parser.add_argument(
            "--resume",
            action="store_true",
            help=(
                "Continue an interrupted run: skip features already indexed "
                "and do not clear the index. Assumes MACHADO_VALID_TYPES is "
                "unchanged since the interrupted run; use --restart after "
                "changing it."
            ),
        )
        parser.add_argument(
            "--restart",
            action="store_true",
            help="Clear the index and rebuild from scratch (the default).",
        )
        parser.add_argument(
            "--max-features",
            type=int,
            default=None,
            help="Stop after N features. For benchmarking.",
        )

    def report(self, message):
        """Write an informational message unless --verbosity 0 was given.

        Django's convention is that verbosity 0 means silent. Writing to
        self.stdout unconditionally ignores that, which makes the test suite
        noisy (the progress dots get interleaved with per-run chatter) and
        makes `--verbosity 0` useless in cron. Route every informational
        message through here; errors still go straight to self.stderr.
        """
        if self.verbosity:
            self.stdout.write(message)

    def handle(self, *args, **options):
        """Rebuild the full-text search index."""
        verbosity = options.get("verbosity", 1)
        self.verbosity = verbosity
        batch_size = int(options.get("batch_size") or 2000)
        resume = bool(options.get("resume"))
        restart = bool(options.get("restart"))
        limit = options.get("max_features")

        if resume and restart:
            raise CommandError("--resume and --restart are mutually exclusive.")
        if batch_size < 1:
            raise CommandError("--batch-size must be at least 1.")

        config = IndexConfig.from_settings()

        start_after = 0
        if resume:
            start_after = (
                FeatureSearchIndex.objects.aggregate(Max("feature_id"))[
                    "feature_id__max"
                ]
                or 0
            )
            if start_after:
                self.report(f"Resuming after feature_id {start_after}.")
        else:
            self.clear_index()

        total = self.count_remaining(config, start_after)
        if limit is not None:
            total = min(total, limit)
        self.report(f"Indexing {total} features...")

        # tqdm defaults to sys.stderr, which a caller redirecting this command's
        # stdout does not capture -- so a test passing stdout=StringIO() still
        # got a progress bar on the terminal. Point the bar at the command's own
        # stream instead, and let disable=None auto-disable it when that stream
        # is not a terminal (test capture, a pipe, cron). verbosity 0 disables
        # it outright.
        #
        # The stream is unwrapped from Django's OutputWrapper deliberately:
        # OutputWrapper.isatty() inherits TextIOBase's hardcoded False, so
        # tqdm would never see a terminal, and its write() appends a newline to
        # every chunk, which would turn the \r-redrawn bar into one line per
        # update.
        stream = getattr(self.stdout, "_out", self.stdout)
        progress = tqdm(
            total=total,
            file=stream,
            disable=True if verbosity == 0 else None,
            desc="Building index",
        )
        indexed = 0
        last_id = start_after
        # Created here, and only here, so the memoised chunk-independent
        # lookups live exactly as long as this run.
        cache = IndexRunCache()
        try:
            for chunk in self.iter_chunks(config, batch_size, start_after, limit):
                ids = [feature.feature_id for feature in chunk]
                ctx = prefetch_chunk(ids, config, cache=cache)
                entries = build_entries(chunk, ctx, config)
                FeatureSearchIndex.objects.bulk_create(
                    entries, batch_size=batch_size, ignore_conflicts=True
                )
                indexed += len(entries)
                last_id = ids[-1]
                progress.update(len(entries))
        except KeyboardInterrupt:
            raise CommandError(
                f"Interrupted after feature_id {last_id} "
                f"({indexed} features indexed). "
                "Re-run with --resume to continue."
            )
        except Exception:
            # Surface where the run died so the operator knows what --resume
            # will pick up; HistoryCommandMixin records the failure itself.
            self.stderr.write(
                f"Failed while indexing the chunk after feature_id "
                f"{last_id} ({indexed} features indexed). "
                "Re-run with --resume to continue from there."
            )
            raise
        finally:
            progress.close()

        self.report(
            self.style.SUCCESS(
                "Search index rebuild completed. "
                "Indexed {} features.".format(indexed)
            )
        )

    def clear_index(self):
        """Empty the index table before a full rebuild.

        TRUNCATE rather than a queryset ``delete()``: on the multi-million-row
        production table, DELETE means one long transaction, gigabytes of WAL,
        and as many dead tuples as rows, which the immediately following
        re-insert then has to work around in a bloated ``fsi_search_gin``.
        Nothing references ``FeatureSearchIndex``, so there is no cascade to
        honour and TRUNCATE is safe here. The count is taken first, purely for
        the operator-facing message.
        """
        stale = FeatureSearchIndex.objects.count()
        # Postgres refuses to TRUNCATE a table with pending deferred FK
        # trigger events, which is the normal state inside a transaction that
        # has already written to it (Django declares FKs DEFERRABLE INITIALLY
        # DEFERRED). Flushing the checks first -- and restoring deferral --
        # makes TRUNCATE legal there. Under the command's real autocommit
        # execution there is nothing pending and this is a no-op.
        connection.check_constraints()
        with connection.cursor() as cursor:
            cursor.execute(
                'TRUNCATE TABLE "{}"'.format(FeatureSearchIndex._meta.db_table)
            )
        if stale:
            self.report(f"  Cleared {stale} stale index entries.")

    def base_queryset(self, config):
        """Return the queryset of features eligible for indexing."""
        return (
            Feature.objects.filter(
                type__name__in=config.valid_types,
                type__cv__name="sequence",
                is_obsolete=False,
            )
            .select_related("organism", "type")
            .order_by("feature_id")
        )

    def count_remaining(self, config, start_after):
        """Count features still to be indexed."""
        return self.base_queryset(config).filter(feature_id__gt=start_after).count()

    def iter_chunks(self, config, batch_size, start_after, limit=None):
        """Yield lists of features using keyset pagination on the PK."""
        last_id = start_after
        produced = 0
        while True:
            remaining = batch_size
            if limit is not None:
                remaining = min(batch_size, limit - produced)
                if remaining <= 0:
                    return
            chunk = list(
                self.base_queryset(config).filter(feature_id__gt=last_id)[:remaining]
            )
            if not chunk:
                return
            yield chunk
            produced += len(chunk)
            last_id = chunk[-1].feature_id
