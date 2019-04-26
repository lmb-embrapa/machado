# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Load Sequence Ontology."""

import obonet
from django.core.management.base import BaseCommand, CommandError
from tqdm import tqdm

from machado.loaders.common import FileValidator
from machado.loaders.exceptions import ImportingError
from machado.loaders.ontology import OntologyLoader


class Command(BaseCommand):
    """Load sequence ontology."""

    help = "Load Sequence Ontology"

    def add_arguments(self, parser):
        """Define the arguments."""
        parser.add_argument(
            "--file",
            help="Sequence Ontology file obo."
            "Available at https://github.com/"
            "The-Sequence-Ontology/SO-Ontologies",
            required=True,
            type=str,
        )

    def handle(self, file: str, verbosity: int = 1, **options):
        """Execute the main function."""
        try:
            FileValidator().validate(file)
        except ImportingError as e:
            raise CommandError(e)

        # Load the ontology file
        with open(file) as obo_file:
            G = obonet.read_obo(obo_file)

        if verbosity > 0:
            self.stdout.write("Preprocessing")

        cv_name = G.graph["default-namespace"][0]
        cv_definition = G.graph["data-version"]

        # Initializing ontology
        ontology = OntologyLoader(cv_name, cv_definition)

        if verbosity > 0:
            self.stdout.write("Loading typedefs")

        # Load typedefs as Dbxrefs and Cvterm
        for typedef in tqdm(
            G.graph["typedefs"], disable=False if verbosity > 0 else True
        ):
            ontology.store_type_def(typedef)

        if verbosity > 0:
            self.stdout.write("Loading terms")

        for n, data in tqdm(
            G.nodes(data=True), disable=False if verbosity > 0 else True
        ):
            ontology.store_term(n, data)

        if verbosity > 0:
            self.stdout.write("Loading relationships")

        for u, v, type in tqdm(
            G.edges(keys=True), disable=False if verbosity > 0 else True
        ):
            ontology.store_relationship(u, v, type)

        if verbosity > 0:
            self.stdout.write(self.style.SUCCESS("Done"))
