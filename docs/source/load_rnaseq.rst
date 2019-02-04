Loading RNA-seq data
====================

Load RNA-seq information
------------------------
Before inserting RNA-seq count tables, it is needed to input information about the experiments and
samples from which the data was generated.
In Machado we will focus on the GEO/NCBI database as a source for RNA-seq experiments information and data.
From the GEO/NCBI database we are supposed to get identifiers for different *series* (e.g.: GSE85653) that
describe the studies/projects as a whole. From the GEO series we can get identifiers for biosamples or, in CHADO
lingo, biomaterials (e.g.: GSM2280286). From the GEO biosamples we get identifiers for RNA-seq experiments
(or assays), usually from the SRA database (e.g.: SRR4033018). SRA identifiers have links for the
raw data one can be interested to analyse.

In Machado, it is necessary to input a .csv file with information for all SRA datafile regarding RNA-seq assays
that will be input.

This file must have the following fields in each line:

"Organism specific name (e.g.: 'Orysa sativa')", "GEO series identifier (e.g: GSE85653)",
"GEO sample identifier (e.g: GSM2280286)", "SRA identifier (e.g: SRR4033018)",
"Experiment description (e.g: 'Heat')", "Sample description (e.g.: 'leaf')",
"Date (in format '%b-%d-%Y': e.g.: Oct-16-2016)".

A sample line for such a file can be seen below:

Orysa sativa,GSE85653,GSM2280286,SRR4033018,Heat,leaf,May-30-2018

To load such a file an example command can be seen below. The databases for the project, biomaterial and assay are required.:

.. code-block:: bash

    python manage.py load_rnaseq_info --filename file.csv --projectdb GEO --biomaterialdb GEO --assaydb SRA

* Loading this file can be faster if you increase the number of threads (--cpu).

.. code-block:: bash

    python manage.py load_rnaseq_info --help

===============        ==================================================================================
--filename 		.csv file *
--projectdb             Project database info (e.g.: 'GEO')
--biomaterialdb         Biomaterial database info (e.g.: 'GEO')
--assaydb               Assay database info (e.g.: 'SRA')
--cpu 			Number of threads
===============        ==================================================================================

\* Any text editor can be used to make such a file.


Remove RNA-seq information
---------------------------

TODO

Load RNA-seq data
------------------------

To load expression count tables for RNA-seq data, a tabular file should be loaded, that can contain data
from several RNA-seq experiments, or assays, per column. This file should have the following header:

"Gene identifier" "SRA Identifier 1" "SRA Identifier 2"  ... "SRA Identifier n"

Example of a header for such a sample file, that contains two assays/experiments:

"gene    SRR5167848.htseq        SRR2302912.htseq"

The body of the table is composed of the gene identifier followed by the counts for each gene, in each experiment.

Example of a line of sucha a sample file:

AT2G44195.1.TAIR10     0.0     0.6936967934559419

Note that the count fields can have floats or integers, depending on the normalization used (usually TPM, FPKM or raw counts).

The gene identifier is supposed to already be loaded as a feature, usually from the organism's genome annotation .gff file.

We used the output of the LSTrAP program as standard format for this file.

.. code-block:: bash

    python manage.py load_rnaseq_data --filename file.tab --organism 'Oryza sativa' --programversion 1.3 --assaydb SRA

* As default the program name is 'LSTrAP' but can be changed with --program
* The data is by default taken as normalized (TPM, FPKM, etc.) but can be changed with --norm
* Loading this file can be faster if you increase the number of threads (--cpu).

.. code-block:: bash

    python manage.py load_rnaseq_data --help

=================      ====================================================================================
--filename               tabular text file with gene counts per line.
--organism               Scientific name (e.g.: 'Oryza sativa')
--programversion         Version of the software (e.g.: '1.3') (string)
--name                   Optional name (string)
--description            Optional description (string)
--algorithm              Optional algorithm description (string)
--assaydb                Optional assay database info (e.g.: 'SRA') (string)
--timeexecuted           Optional Date software was run. Mandatory format: e.g.:
                            'Oct-16-2016' (string)
--program                Optional Name of the software (default: 'LSTrAP') (string)
--norm                   Optional Normalized data: 1-yes (tpm, fpkm, etc.); 0-no (raw
                            counts); default is 1) (integer)
=================      ====================================================================================

Remove RNA-seq data
---------------------------

TODO
