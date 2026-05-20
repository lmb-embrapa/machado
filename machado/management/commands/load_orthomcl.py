# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Load OrthoMCL groups.txt result."""

from machado.models import Cv, Db, Dbxref, Cvterm
import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

from django.core.management.base import BaseCommand, CommandError
from machado.management.commands._base import HistoryCommandMixin
from tqdm import tqdm

from machado.loaders.common import FileValidator
from machado.loaders.feature import MultispeciesFeatureLoader


class Command(HistoryCommandMixin, BaseCommand):
    """Load OrthoMCL groups.txt results."""

    help = "Load OrthoMCL 'groups.txt' result file" ""

    def add_arguments(self, parser):
        """Define the arguments."""
        parser.add_argument(
            "--file", help="Path to the 'groups.txt' file", required=True, type=str
        )
        parser.add_argument(
            "--cpu",
            help="Number of threads for parallel processing",
            default=1,
            type=int,
        )

    def handle(self, file: str, cpu: int = 1, verbosity: int = 0, **options):
        """Execute the main function."""
        FileValidator().validate(file)
        filename = os.path.basename(file)
        if verbosity > 0:
            self.stdout.write("Processing file: {}".format(filename))
        groups = open(file, "r")
        # retrieve only the file name
        pool = ThreadPoolExecutor(max_workers=cpu)
        tasks = list()
        cv, created = Cv.objects.get_or_create(name="feature_property")
        ortho_db, created = Db.objects.get_or_create(name="ORTHOMCL_SOURCE")
        ortho_dbxref, created = Dbxref.objects.get_or_create(
            accession="ORTHOMCL_SOURCE", db=ortho_db
        )
        cvterm_cluster, created = Cvterm.objects.get_or_create(
            name="orthologous group",
            cv=cv,
            dbxref=ortho_dbxref,
            is_obsolete=0,
            is_relationshiptype=0,
        )

        # hardcoded as orthomcl uses protein input
        soterm = "polypeptide"

        source = "null"
        featureloader = MultispeciesFeatureLoader(source=source, filename=filename)
        # each line is an orthologous group
        for line in groups:
            members = []
            name = ""
            fields = re.split(r"\s+", line.strip())

            # cluster must have at least two fields, one cluster ID (name) and at least one member ID.
            if len(fields) > 1:
                name = fields[0]
                fields.pop(0)
                for field in fields:
                    members.append(field)
            else:
                raise CommandError(
                    "Invalid cluster file format. Please check the input file."
                )
            # only orthologous groups with 2 or more members allowed
            if len(members) > 1:
                tasks.append(
                    pool.submit(
                        featureloader.store_feature_groups,
                        soterm=soterm,
                        group=members,
                        term=cvterm_cluster.cvterm_id,
                        value=name,
                    )
                )
        if verbosity > 0:
            self.stdout.write("Loading data...")
        for task in tqdm(as_completed(tasks), total=len(tasks), disable=verbosity == 0):
            if task.result():
                e = task.result()
                raise (e)
        pool.shutdown()
        if verbosity > 0:
            self.stdout.write(
                self.style.SUCCESS("Successfully processed {}".format(filename))
            )
