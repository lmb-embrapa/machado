Loading Blast results
=====================

In order to load a Blast results file, both the query and the subject records must be previously stored.

Load Blast
----------

.. code-block:: bash

    python manage.py load_blast --file blast_result.xml --so_query mRNA --so_subject assembly --program blastn --version 2.2.31+

* Loading this file can be faster if you increase the number of threads (--cpu).

.. code-block:: bash

    python manage.py load_gff --help

================   ===================================================================
--file 			   Blast XML file *
--so_query         Query Sequence Ontology term. (eg. assembly, mRNA, polypeptide) *
--so_subject       Subject Sequence Ontology term. (eg. assembly, mRNA, polypeptide) *
--program          Program *
--programversion   Program version *
--name             Name
--description      Description
--algorithm        Algorithm
--cpu 			   Number of threads
================   ===================================================================

\* required fields


Remove file
-----------

If, by any reason, you need to remove a Blast result set you should use the command *remove_analysis*.

.. code-block:: bash

    python manage.py remove_analysis --help

* This command requires the analysis name (Analysis.sourcename)
