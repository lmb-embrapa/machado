# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Load views."""
from django.conf import settings
from django.core.management import call_command

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from machado.api.serializers import load as loadSerializers

from rest_framework import viewsets
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from tempfile import NamedTemporaryFile
from threading import Thread


class OrganismViewSet(viewsets.GenericViewSet):
    """ViewSet for loading organism."""

    serializer_class = loadSerializers.OrganismSerializer
    permission_classes = [IsAuthenticated]
    operation_summary = "Load organism"
    operation_description = operation_summary + "<br /><br />"
    if hasattr(settings, "MACHADO_EXAMPLE_ORGANISM_COMMON_NAME"):
        operation_description += "<b>Example:</b><br />common_name={}".format(
            settings.MACHADO_EXAMPLE_ORGANISM_COMMON_NAME
        )

    request_body = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "genus": openapi.Schema(type=openapi.TYPE_STRING, description="Genus"),
            "species": openapi.Schema(type=openapi.TYPE_STRING, description="Species"),
            "infraspecific_name": openapi.Schema(
                type=openapi.TYPE_STRING, description="Infraspecific name"
            ),
            "abbreviation": openapi.Schema(
                type=openapi.TYPE_STRING, description="Abbreviation"
            ),
            "common_name": openapi.Schema(
                type=openapi.TYPE_STRING, description="Common name"
            ),
            "comment": openapi.Schema(type=openapi.TYPE_STRING, description="Comment"),
        },
    )

    @swagger_auto_schema(
        request_body=request_body,
        operation_summary=operation_summary,
        operation_description=operation_description,
    )
    def create(self, request):
        """Handle the POST request for loading organism."""
        genus = request.data.get("genus")
        species = request.data.get("species")
        abbreviation = request.data.get("abbreviation")
        common_name = request.data.get("common_name")
        infraspecific_name = request.data.get("infraspecific_name")
        comment = request.data.get("comment")

        if not genus or not species:
            return Response(
                {"error": "Genus and species are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        thread = Thread(
            target=call_command,
            args=("insert_organism",),
            kwargs=(
                {
                    "genus": genus,
                    "species": species,
                    "abbreviation": abbreviation,
                    "common_name": common_name,
                    "infraspecific_name": infraspecific_name,
                    "comment": comment,
                }
            ),
            daemon=True,
        )

        thread.start()

        return Response(
            {
                "status": "Submited successfully",
                "call_command": "insert_organism",
            },
            status=status.HTTP_200_OK,
        )


class RelationsOntologyViewSet(viewsets.GenericViewSet):
    """ViewSet for loading relations ontology."""

    serializer_class = loadSerializers.FileSerializer
    permission_classes = [IsAuthenticated]
    operation_summary = "Load relations ontology"
    operation_description = operation_summary + "<br /><br />"
    operation_description += "<li>URL: https://github.com/oborel/obo-relations</li>"
    operation_description += "<li>File: ro.obo</li>"

    file_param = openapi.Parameter(
        "file",
        openapi.IN_QUERY,
        description="so.obo file",
        required=True,
        type=openapi.TYPE_FILE,
    )

    @swagger_auto_schema(
        manual_parameters=[
            file_param,
        ],
        operation_summary=operation_summary,
        operation_description=operation_description,
    )
    def create(self, request):
        """Handle the POST request for loading organism."""
        file = request.data.get("file")
        file_content = file.read()

        with NamedTemporaryFile(mode="w", delete=True) as temp_file:
            temp_file.write(file_content)
            call_command("load_relations_ontology", file=temp_file.name)

#        thread = Thread(
#            target=call_command,
#            args=("load_relations_ontology",),
#            kwargs=(
#                {
#                    "file": file,
#                    "verbosity": 0,
#                }
#            ),
#            daemon=True,
#        )
#
#        thread.start()

        return Response(
            {
                "status": "Submited successfully",
                "call_command": "load_relations_ontology",
            },
            status=status.HTTP_200_OK,
        )
