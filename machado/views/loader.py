import os
import sys
import threading
import subprocess
import urllib.request
import tempfile
from django.core.management import call_command
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views import View
from django.urls import reverse
from machado.models import Organism, Db, Analysis, History, Cv, Cvterm, Dbxrefprop

# Define the ordered sequence of commands and their parameters
COMMANDS_CONFIG = {
    "load_relations_ontology": {
        "help": "Load relationship types (OBO format) into the database",
        "args": [
            {
                "name": "file",
                "required": True,
                "default": None,
                "help": "Path to the relationship OBO file",
                "type": "file"
            }
        ],
        "title": "Load Relations Ontology"
    },
    "load_sequence_ontology": {
        "help": "Load Sequence Ontology (SO) from an OBO file",
        "args": [
            {
                "name": "file",
                "required": True,
                "default": None,
                "help": "Path to the Sequence Ontology OBO file",
                "type": "file"
            }
        ],
        "title": "Load Sequence Ontology"
    },
    "load_gene_ontology": {
        "help": "Load Gene Ontology (GO) terms and definitions from an OBO file",
        "args": [
            {
                "name": "file",
                "required": True,
                "default": None,
                "help": "Path to the Gene Ontology OBO file",
                "type": "file"
            },
            {
                "name": "cpu",
                "required": False,
                "default": 1,
                "help": "Number of threads for parallel processing",
                "type": "text"
            }
        ],
        "title": "Load Gene Ontology"
    },
    "load_publication": {
        "help": "Load publication metadata (e.g., title, year, journal) from a file",
        "args": [
            {
                "name": "file",
                "required": True,
                "default": None,
                "help": "Path to the publication data file",
                "type": "file"
            },
            {
                "name": "cpu",
                "required": False,
                "default": 1,
                "help": "Number of threads for parallel processing",
                "type": "text"
            }
        ],
        "title": "Load Publication"
    },
    "insert_organism": {
        "help": "Manually register a new organism in the database",
        "args": [
            {
                "name": "abbreviation",
                "required": False,
                "default": None,
                "help": "Organism abbreviation (e.g., H.sapiens)",
                "type": "text"
            },
            {
                "name": "genus",
                "required": True,
                "default": None,
                "help": "Genus name (e.g., Homo)",
                "type": "text"
            },
            {
                "name": "species",
                "required": True,
                "default": None,
                "help": "Species name (e.g., sapiens)",
                "type": "text"
            },
            {
                "name": "common_name",
                "required": False,
                "default": None,
                "help": "Common name (e.g., human)",
                "type": "text"
            },
            {
                "name": "infraspecific_name",
                "required": False,
                "default": None,
                "help": "Infraspecific name (e.g., subspecies, variety)",
                "type": "text"
            },
            {
                "name": "comment",
                "required": False,
                "default": None,
                "help": "Additional comments",
                "type": "text"
            }
        ],
        "title": "Insert Organism"
    },
    "load_organism_publication": {
        "help": "Link organisms to publications from a tab-separated file",
        "args": [
            {
                "name": "file",
                "required": True,
                "default": None,
                "help": "Path to the tab-separated file (format: genus species\tDOI)",
                "type": "file"
            },
            {
                "name": "cpu",
                "required": False,
                "default": 1,
                "help": "Number of threads for parallel processing",
                "type": "text"
            }
        ],
        "title": "Load Organism Publication"
    },
    "load_fasta": {
        "help": "Load sequences from a FASTA file into the database",
        "args": [
            {
                "name": "file",
                "required": True,
                "default": None,
                "help": "Path to the FASTA file",
                "type": "file"
            },
            {
                "name": "organism",
                "required": True,
                "default": None,
                "help": "Scientific name of the species",
                "type": "organism"
            },
            {
                "name": "soterm",
                "required": True,
                "default": None,
                "help": "Sequence Ontology (SO) term",
                "type": "soterm",
                "label": "SO Term"
            },
            {
                "name": "nosequence",
                "required": False,
                "default": None,
                "help": "Register name only",
                "type": "checkbox",
                "label": "No Sequence"
            },
            {
                "name": "cpu",
                "required": False,
                "default": 1,
                "help": "Number of threads for parallel processing",
                "type": "text"
            },
            {
                "name": "description",
                "required": False,
                "default": None,
                "help": "Source description",
                "type": "text"
            },
            {
                "name": "url",
                "required": False,
                "default": None,
                "help": "URL of the sequence source",
                "type": "text"
            },
            {
                "name": "doi",
                "required": False,
                "default": None,
                "help": "DOI reference",
                "type": "text"
            }
        ],
        "title": "Load FASTA"
    },
    "load_gff": {
        "help": "Load gene annotations from a GFF3 file",
        "args": [
            {
                "name": "file",
                "required": True,
                "default": None,
                "help": "Path to the GFF3 file",
                "type": "file"
            },
            {
                "name": "index",
                "required": False,
                "default": None,
                "help": "Optional: Tabix index file (.tbi or .csi). Required if GFF is compressed.",
                "type": "file"
            },
            {
                "name": "organism",
                "required": True,
                "default": None,
                "help": "Scientific name of the species (e.g., Homo sapiens)",
                "type": "organism"
            },
            {
                "name": "ignore",
                "required": False,
                "default": None,
                "help": "List of GFF types to ignore (comma-separated)",
                "type": "text"
            },
            {
                "name": "qtl",
                "required": False,
                "default": None,
                "help": "Load features as QTLs",
                "type": "checkbox",
                "label": "QTL Mode"
            },
            {
                "name": "doi",
                "required": False,
                "default": None,
                "help": "DOI of the reference article",
                "type": "text"
            },
            {
                "name": "cpu",
                "required": False,
                "default": 1,
                "help": "Number of threads for parallel processing",
                "type": "text"
            }
        ],
        "title": "Load GFF3"
    },
    "load_feature_annotation": {
        "help": "Load feature annotations (properties) from a result file",
        "args": [
            {
                "name": "file",
                "required": True,
                "default": None,
                "help": "Path to the annotation file (format: uniquename\tvalue)",
                "type": "file"
            },
            {
                "name": "organism",
                "required": True,
                "default": None,
                "help": "Scientific name of the species (e.g., Homo sapiens)",
                "type": "organism"
            },
            {
                "name": "soterm",
                "required": True,
                "default": None,
                "help": "Sequence Ontology (SO) term of the features",
                "type": "soterm",
                "label": "SO Term"
            },
            {
                "name": "cvterm",
                "required": True,
                "default": None,
                "help": "Name of the feature property term (e.g., 'product', 'alias')",
                "type": "text"
            },
            {
                "name": "doi",
                "required": False,
                "default": None,
                "help": "DOI of the reference article",
                "type": "text"
            },
            {
                "name": "cpu",
                "required": False,
                "default": 1,
                "help": "Number of threads for parallel processing",
                "type": "text"
            },
            {
                "name": "ignorenotfound",
                "required": False,
                "default": None,
                "help": "Continue if feature is not found",
                "type": "checkbox",
                "label": "Ignore Not Found"
            }
        ],
        "title": "Load Feature Annotation"
    },
    "load_feature_dbxrefs": {
        "help": "Load database cross-references (DBxRefs) for features",
        "args": [
            {
                "name": "file",
                "required": True,
                "default": None,
                "help": "Path to the tab-separated file",
                "type": "file"
            },
            {
                "name": "organism",
                "required": True,
                "default": None,
                "help": "Scientific name of the species",
                "type": "organism"
            },
            {
                "name": "soterm",
                "required": True,
                "default": None,
                "help": "Sequence Ontology (SO) term",
                "type": "soterm",
                "label": "SO Term"
            },
            {
                "name": "cpu",
                "required": False,
                "default": 1,
                "help": "Number of threads for parallel processing",
                "type": "text"
            },
            {
                "name": "ignorenotfound",
                "required": False,
                "default": None,
                "help": "Continue if feature not found",
                "type": "text"
            }
        ],
        "title": "Load Feature DBxRefs"
    },
    "load_feature_publication": {
        "help": "Link features to publications from a tab-separated file",
        "args": [
            {
                "name": "file",
                "required": True,
                "default": None,
                "help": "Path to the tab-separated file (format: feature_uniquename\tDOI)",
                "type": "file"
            },
            {
                "name": "organism",
                "required": True,
                "default": None,
                "help": "Scientific name of the species (e.g., Homo sapiens)",
                "type": "organism"
            },
            {
                "name": "soterm",
                "required": True,
                "default": None,
                "help": "Sequence Ontology (SO) term of the features",
                "type": "soterm",
                "label": "SO Term"
            },
            {
                "name": "cpu",
                "required": False,
                "default": 1,
                "help": "Number of threads for parallel processing",
                "type": "text"
            }
        ],
        "title": "Load Feature Publication"
    },
    "load_feature_sequence": {
        "help": "Load sequence residues for existing features from a FASTA file",
        "args": [
            {
                "name": "file",
                "required": True,
                "default": None,
                "help": "Path to the FASTA file",
                "type": "file"
            },
            {
                "name": "soterm",
                "required": True,
                "default": None,
                "help": "Sequence Ontology (SO) term of the features",
                "type": "soterm",
                "label": "SO Term"
            },
            {
                "name": "organism",
                "required": True,
                "default": None,
                "help": "Scientific name of the species (e.g., Homo sapiens)",
                "type": "organism"
            },
            {
                "name": "cpu",
                "required": False,
                "default": 1,
                "help": "Number of threads for parallel processing",
                "type": "text"
            }
        ],
        "title": "Load Feature Sequence"
    },
    "load_similarity_matches": {
        "help": "Load pre-calculated similarity matches (match/match_part) from a file",
        "args": [
            {
                "name": "file",
                "required": True,
                "default": None,
                "help": "Path to the similarity matches file",
                "type": "file"
            },
            {
                "name": "format",
                "required": True,
                "default": None,
                "help": "Format of the input file",
                "type": "text"
            },
            {
                "name": "cpu",
                "required": False,
                "default": 1,
                "help": "Number of threads for parallel processing",
                "type": "text"
            }
        ],
        "title": "Load Similarity Matches"
    },
    "load_similarity": {
        "help": "Load sequence similarity results (e.g., BLAST) into the database",
        "args": [
            {
                "name": "file",
                "required": True,
                "default": None,
                "help": "Path to the similarity result file",
                "type": "file"
            },
            {
                "name": "format",
                "required": True,
                "default": None,
                "help": "Format of the input file (e.g., 'blastxml', 'tabular')",
                "type": "text"
            },
            {
                "name": "so_query",
                "required": True,
                "default": None,
                "help": "SO term of the query features",
                "type": "soterm",
                "label": "Query SO Term"
            },
            {
                "name": "so_subject",
                "required": True,
                "default": None,
                "help": "SO term of the subject features",
                "type": "soterm",
                "label": "Subject SO Term"
            },
            {
                "name": "organism_query",
                "required": True,
                "default": None,
                "help": "Organism name of the query features",
                "type": "organism"
            },
            {
                "name": "organism_subject",
                "required": True,
                "default": None,
                "help": "Organism name of the subject features",
                "type": "organism"
            },
            {
                "name": "program",
                "required": True,
                "default": None,
                "help": "Program used (e.g., 'blastp')",
                "type": "text"
            },
            {
                "name": "programversion",
                "required": True,
                "default": None,
                "help": "Version of the program",
                "type": "text"
            },
            {
                "name": "name",
                "required": False,
                "default": None,
                "help": "Analysis name",
                "type": "text"
            },
            {
                "name": "description",
                "required": False,
                "default": None,
                "help": "Analysis description",
                "type": "text"
            },
            {
                "name": "algorithm",
                "required": False,
                "default": None,
                "help": "Algorithm used",
                "type": "text"
            },
            {
                "name": "cpu",
                "required": False,
                "default": 1,
                "help": "Number of threads for parallel processing",
                "type": "text"
            }
        ],
        "title": "Load Similarity"
    },
    "load_orthomcl": {
        "help": "Load OrthoMCL 'groups.txt' result file",
        "args": [
            {
                "name": "file",
                "required": True,
                "default": None,
                "help": "Path to the 'groups.txt' file",
                "type": "file"
            },
            {
                "name": "cpu",
                "required": False,
                "default": 1,
                "help": "Number of threads for parallel processing",
                "type": "text"
            }
        ],
        "title": "Load OrthoMCL"
    },
    "load_rnaseq_info": {
        "help": "Load RNA-seq .csv information file",
        "args": [
            {
                "name": "file",
                "required": True,
                "default": None,
                "help": "Path to the CSV file",
                "type": "file"
            },
            {
                "name": "biomaterialdb",
                "required": True,
                "default": None,
                "help": "Database name for biomaterials",
                "type": "text"
            },
            {
                "name": "assaydb",
                "required": True,
                "default": None,
                "help": "Database name for assays",
                "type": "text"
            },
            {
                "name": "cpu",
                "required": False,
                "default": 1,
                "help": "Number of threads for parallel processing",
                "type": "text"
            }
        ],
        "title": "Load RNA-Seq Info"
    },
    "load_rnaseq_data": {
        "help": "Load RNA-Seq expression data into the database",
        "args": [
            {
                "name": "file",
                "required": True,
                "default": None,
                "help": "Path to the expression data file",
                "type": "file"
            },
            {
                "name": "organism",
                "required": True,
                "default": None,
                "help": "Scientific name of the species (e.g., Homo sapiens)",
                "type": "organism"
            },
            {
                "name": "programversion",
                "required": True,
                "default": None,
                "help": "Version of the program used to generate the data",
                "type": "text"
            },
            {
                "name": "name",
                "required": False,
                "default": None,
                "help": "Analysis name",
                "type": "text"
            },
            {
                "name": "description",
                "required": False,
                "default": None,
                "help": "Analysis description",
                "type": "text"
            },
            {
                "name": "algorithm",
                "required": False,
                "default": None,
                "help": "Algorithm used for quantification",
                "type": "text"
            },
            {
                "name": "assaydb",
                "required": False,
                "default": None,
                "help": "Database for assay accessions (e.g., 'SRA')",
                "type": "text"
            },
            {
                "name": "timeexecuted",
                "required": False,
                "default": None,
                "help": "Time of execution (YYYY-MM-DD)",
                "type": "text"
            },
            {
                "name": "program",
                "required": False,
                "default": "LSTrAP",
                "help": "Program name (default: LSTrAP)",
                "type": "text"
            },
            {
                "name": "norm",
                "required": False,
                "default": 1,
                "help": "Normalization method (1: FPKM, 2: TPM, 3: Counts)",
                "type": "text"
            },
            {
                "name": "ignorenotfound",
                "required": False,
                "default": None,
                "help": "Continue if feature is not found",
                "type": "checkbox",
                "label": "Ignore Not Found"
            },
            {
                "name": "cpu",
                "required": False,
                "default": 1,
                "help": "Number of threads for parallel processing",
                "type": "text"
            }
        ],
        "title": "Load RNA-Seq Data"
    },
    "load_coexpression_clusters": {
        "help": "Load co-expression clusters and their member features",
        "args": [
            {
                "name": "file",
                "required": True,
                "default": None,
                "help": "Path to the co-expression clusters file",
                "type": "file"
            },
            {
                "name": "soterm",
                "required": False,
                "default": "mRNA",
                "help": "SO term of the features (default: mRNA)",
                "type": "text"
            },
            {
                "name": "organism",
                "required": True,
                "default": None,
                "help": "Scientific name of the species (e.g., Homo sapiens)",
                "type": "organism"
            },
            {
                "name": "cpu",
                "required": False,
                "default": 1,
                "help": "Number of threads for parallel processing",
                "type": "text"
            }
        ],
        "title": "Load Co-expression Clusters"
    },
    "load_coexpression_pairs": {
        "help": "Load co-expression gene pairs from a result file",
        "args": [
            {
                "name": "file",
                "required": True,
                "default": None,
                "help": "Path to the co-expression pairs file",
                "type": "file"
            },
            {
                "name": "organism",
                "required": True,
                "default": None,
                "help": "Scientific name of the species (e.g., Homo sapiens)",
                "type": "organism"
            },
            {
                "name": "soterm",
                "required": False,
                "default": "mRNA",
                "help": "SO term of the features (default: mRNA)",
                "type": "text"
            },
            {
                "name": "cpu",
                "required": False,
                "default": 1,
                "help": "Number of threads for parallel processing",
                "type": "text"
            }
        ],
        "title": "Load Co-expression Pairs"
    },
    "load_vcf": {
        "help": "Load genetic variants from a VCF file",
        "args": [
            {
                "name": "file",
                "required": True,
                "default": None,
                "help": "Path to the VCF file",
                "type": "file"
            },
            {
                "name": "organism",
                "required": True,
                "default": None,
                "help": "Scientific name of the species (e.g., Homo sapiens)",
                "type": "organism"
            },
            {
                "name": "doi",
                "required": False,
                "default": None,
                "help": "DOI of the reference article",
                "type": "text"
            },
            {
                "name": "cpu",
                "required": False,
                "default": 1,
                "help": "Number of threads for parallel processing",
                "type": "text"
            }
        ],
        "title": "Load VCF"
    },
    "rebuild_search_index": {
        "help": "Rebuild the PostgreSQL full-text search index for features.",
        "args": [
            {
                "name": "batch_size",
                "required": False,
                "default": 1000,
                "help": "Number of records per bulk insert",
                "type": "text"
            }
        ],
        "title": "Rebuild Search Index"
    },
    "check_ids": {
        "help": "Verify the existence of feature IDs in the database",
        "args": [
            {
                "name": "file",
                "required": True,
                "default": None,
                "help": "Path to the file containing IDs",
                "type": "file"
            },
            {
                "name": "organism",
                "required": True,
                "default": None,
                "help": "Scientific name of the species",
                "type": "organism"
            },
            {
                "name": "soterms",
                "required": True,
                "default": None,
                "help": "SO terms to check",
                "type": "soterm",
                "label": "SO Term"
            }
        ],
        "title": "Check IDs"
    },
    "remove_organism": {
        "help": "Remove an organism from the database",
        "args": [
            {
                "name": "organism",
                "required": True,
                "default": None,
                "help": "Scientific name of the species (e.g., Homo sapiens)",
                "type": "organism"
            }
        ],
        "title": "Remove Organism"
    },
    "remove_analysis": {
        "help": "Remove an analysis and all its associated data (CASCADE)",
        "args": [
            {
                "name": "name",
                "required": True,
                "default": None,
                "help": "Name of the analysis to remove",
                "type": "text"
            }
        ],
        "title": "Remove Analysis"
    },
    "remove_publication": {
        "help": "Remove a publication and its associated references from the database",
        "args": [
            {
                "name": "doi",
                "required": True,
                "default": None,
                "help": "DOI of the publication to remove",
                "type": "text"
            }
        ],
        "title": "Remove Publication"
    },
    "remove_ontology": {
        "help": "Remove an ontology and all its associated terms (CASCADE)",
        "args": [
            {
                "name": "name",
                "required": True,
                "default": None,
                "help": "Name of the ontology to remove",
                "type": "ontology"
            }
        ],
        "title": "Remove Ontology"
    },
    "remove_feature_annotation": {
        "help": "Remove feature annotations (properties) of a specific type",
        "args": [
            {
                "name": "organism",
                "required": False,
                "default": None,
                "help": "Scientific name of the species (optional)",
                "type": "organism"
            },
            {
                "name": "cvterm",
                "required": True,
                "default": None,
                "help": "Name of the feature property term (e.g., 'product', 'alias')",
                "type": "text"
            }
        ],
        "title": "Remove Feature Annotation"
    },
    "remove_relationship": {
        "help": "Remove feature relationships associated with a specific file",
        "args": [
            {
                "name": "file",
                "required": True,
                "default": None,
                "help": "Path to the file whose relationships should be removed",
                "type": "file"
            }
        ],
        "title": "Remove Relationship"
    },
    "remove_file": {
        "help": "Remove records and associated data linked to a specific file (CASCADE)",
        "args": [
            {
                "name": "name",
                "required": True,
                "default": None,
                "help": "Select the file to remove all associated records",
                "type": "uploaded_file"
            }
        ],
        "title": "Remove File"
    }
}

class DashboardView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, "loader/dashboard.html", {"commands": COMMANDS_CONFIG})

class CommandFormView(LoginRequiredMixin, View):
    def get(self, request, command_name):
        config = COMMANDS_CONFIG.get(command_name)
        if not config:
            return redirect("loader_dashboard")
        
        # Populate dynamic fields
        context = {"command_name": command_name, "config": config}
        for arg in config["args"]:
            if arg["type"] == "organism":
                context["organisms"] = Organism.objects.exclude(genus="multispecies", species="multispecies")
            elif arg["type"] == "ontology":
                context["ontologies"] = Cv.objects.all().order_by("name")
            elif arg["type"] == "soterm":
                context["soterms"] = Cvterm.objects.filter(cv__name="sequence").order_by("name")
            elif arg["type"] == "uploaded_file":
                context["uploaded_files"] = Dbxrefprop.objects.filter(
                    type__name="located in", 
                    type__cv__name="relationship"
                ).values_list("value", flat=True).distinct().order_by("value")
        
        return render(request, "loader/command_form.html", context)

    def post(self, request, command_name):
        config = COMMANDS_CONFIG.get(command_name)
        if not config:
            return redirect("loader_dashboard")

        command_kwargs = {}
        upload_dir = os.path.join(tempfile.gettempdir(), "machado_uploads")
        os.makedirs(upload_dir, exist_ok=True)

        for arg in config["args"]:
            if arg["type"] == "file":
                # Check for file upload or URL
                uploaded_file = request.FILES.get(arg["name"] + "_upload")
                file_url = request.POST.get(arg["name"] + "_url")
                file_path = ""

                if uploaded_file:
                    file_path = os.path.join(upload_dir, uploaded_file.name)
                    with open(file_path, "wb+") as destination:
                        for chunk in uploaded_file.chunks():
                            destination.write(chunk)
                elif file_url:
                    try:
                        file_name = file_url.split("/")[-1]
                        file_path = os.path.join(upload_dir, file_name)
                        # Use a more common User-Agent to avoid blocks/redirect issues
                        req = urllib.request.Request(
                            file_url, 
                            headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
                        )
                        with urllib.request.urlopen(req) as response, open(file_path, "wb") as out_file:
                            out_file.write(response.read())
                    except Exception as e:
                        messages.error(request, f"Failed to download remote file: {str(e)}")
                        return redirect("loader_command_form", command_name=command_name)
                
                if arg["required"] and not file_path:
                    messages.error(request, f"The file for '{arg['name']}' is required. Please upload a file or provide a URL.")
                    return redirect("loader_command_form", command_name=command_name)

                if file_path and arg["name"] != "index":
                    command_kwargs[arg["name"]] = file_path
            else:
                val = request.POST.get(arg["name"])
                if arg["required"] and not val:
                    messages.error(request, f"Argument '{arg['name']}' is required.")
                    return redirect("loader_command_form", command_name=command_name)

                if val:
                    val = val.strip()
                    if arg["type"] == "organism":
                        try:
                            org = Organism.objects.get(pk=int(val))
                            if org.infraspecific_name:
                                val = f"{org.genus} {org.species} {org.infraspecific_name}"
                            else:
                                val = f"{org.genus} {org.species}"
                        except Organism.DoesNotExist:
                            pass
                    elif arg["type"] == "ontology":
                        try:
                            cv = Cv.objects.get(pk=int(val))
                            val = cv.name
                        except Cv.DoesNotExist:
                            pass
                    elif arg["type"] == "checkbox":
                        val = True if val else False
                    elif arg["type"] == "soterm":
                        try:
                            term = Cvterm.objects.get(pk=int(val))
                            val = term.name
                        except Cvterm.DoesNotExist:
                            pass
                    elif str(val).replace(",", "").isdigit():
                        val = int(str(val).replace(",", ""))
                    command_kwargs[arg["name"]] = val
        
        # Create History record
        history = History.objects.create(command=command_name, params=str(command_kwargs), status="PENDING")

        def run_subprocess():
            # Find manage.py path
            # BASE_DIR is usually the project root in a standard Django setup
            manage_py_path = os.path.join(settings.BASE_DIR, "manage.py")
            
            if not os.path.exists(manage_py_path):
                # Try project_template subdirectory (common in machado dev environment)
                manage_py_path = os.path.join(settings.BASE_DIR, "project_template", "manage.py")
            
            if not os.path.exists(manage_py_path):
                # Try to find it in the parent of settings.BASE_DIR if needed, 
                # but let's stick to abspath fallback
                manage_py_path = os.path.abspath("manage.py")

            manage_py_path = os.path.abspath(manage_py_path)

            cmd = [sys.executable, manage_py_path, command_name]
            for k, v in command_kwargs.items():
                if isinstance(v, bool):
                    if v:
                        cmd.append(f"--{k}")
                else:
                    cmd.append(f"--{k}")
                    cmd.append(str(v))
            
            # Ensure verbosity is set to 1 to keep useful output
            if "verbosity" not in command_kwargs:
                cmd.extend(["--verbosity", "1"])

            env = os.environ.copy()
            env["MACHADO_HISTORY_ID"] = str(history.history_id)
            env["PYTHONUNBUFFERED"] = "1"

            try:
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    env=env,
                    cwd=os.path.dirname(os.path.abspath(manage_py_path))
                )
                
                history.pid = process.pid
                history.status = "RUNNING"
                history.save()

                stdout_data, stderr_data = process.communicate()
                
                # Filter out tqdm progress bars from output
                def clean_output(text):
                    if not text: return text
                    import re
                    # Split by both \r and \n to handle tqdm updates
                    lines = text.replace('\r', '\n').split('\n')
                    cleaned_lines = []
                    for line in lines:
                        # tqdm progress bar pattern detection
                        if re.search(r'\d+%.*?\|.*?\|', line):
                            continue
                        if line.strip():
                            cleaned_lines.append(line)
                    return '\n'.join(cleaned_lines).strip()

                stdout_data = clean_output(stdout_data)
                stderr_data = clean_output(stderr_data)

                # Truncate if necessary (limit to 100,000 characters)
                limit = 100000
                if stdout_data and len(stdout_data) > limit:
                    stdout_data = "...(truncated)...\n" + stdout_data[-limit:]
                if stderr_data and len(stderr_data) > limit:
                    stderr_data = "...(truncated)...\n" + stderr_data[-limit:]

                if process.returncode == 0:
                    history.success(stdout=stdout_data, stderr=stderr_data)
                else:
                    history.failure(stdout=stdout_data, stderr=stderr_data, exit_code=process.returncode)
            except Exception as e:
                history.failure(stderr=str(e))

        threading.Thread(target=run_subprocess).start()

        messages.success(request, f"Command '{config['title']}' submitted successfully. Check its status below.")
        return redirect("loader_history")

class HistoryListView(LoginRequiredMixin, View):
    def get(self, request):
        histories = History.objects.all().order_by("-created_at")[:50]
        
        # Check for DEAD processes
        import os
        for h in histories:
            if h.status == "RUNNING" and h.pid:
                try:
                    # Check if process exists (signal 0 doesn't kill it)
                    os.kill(h.pid, 0)
                except OSError:
                    # Process is not running
                    h.status = "DEAD"
                    h.save()
                    
        any_running = any(h.status == "RUNNING" for h in histories)
        return render(request, "loader/history.html", {"histories": histories, "any_running": any_running})
