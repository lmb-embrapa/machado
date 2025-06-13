# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Load OrthoMCL groups.txt result."""

import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

from django.core.management.base import BaseCommand, CommandError
from tqdm import tqdm

from machado.loaders.common import FileValidator
from machado.loaders.exceptions import ImportingError
from machado.loaders.feature import MultispeciesFeatureLoader
from machado.models import Cv, Cvterm, Dbxref, Db, History


class Command(BaseCommand):
    """Load OrthoMCL groups.txt results."""

    help = """Load 'groups.txt' output result file from orthoMCL.
The 'groups.txt' file is headless and have the format as follows:
nameofthegroup1: featuremember1 featuremember2 featuremember3
nameofthegroup2: featuremember4 featuremember5 ...
and so on.
The feature members need to be loaded previously."""

    def add_arguments(self, parser):
        """Define the arguments."""
        parser.add_argument("--file", help="'groups.txt' File", required=True, type=str)
        parser.add_argument("--cpu", help="Number of threads", default=1, type=int)

    def handle(self, file: str, cpu: int = 1, verbosity: int = 0, **options):
        """Execute the main function."""
        history_obj = History()
        history_obj.start(command="load_orthomcl", params=locals())
        try:
            FileValidator().validate(file)
        except ImportingError as e:
            history_obj.failure(description=str(e))
            raise CommandError(e)

        filename = os.path.basename(file)
        if verbosity > 0:
            self.stdout.write("Processing file: {}".format(filename))
        try:
            groups = open(file, "r")
            # retrieve only the file name
        except ImportingError as e:
            history_obj.failure(description=str(e))
            raise CommandError(e)
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
                history_obj.failure(
                    description="Cluster file has fields problems. Please, check."
                )
                raise CommandError("Cluster file has fields problems. Please, check.")
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
            self.stdout.write("Loading")
        for task in tqdm(as_completed(tasks), total=len(tasks)):
            if task.result():
                e = task.result()
                history_obj.failure(description=str(e))
                raise (e)
        pool.shutdown()
        history_obj.success(description="Done")
        if verbosity > 0:
            self.stdout.write(self.style.SUCCESS("Done with {}".format(filename)))
