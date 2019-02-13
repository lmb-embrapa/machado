Loading Blast results
=====================

In order to load a BLAST xml result file, both the query and the subject records must be previously stored (see below). The current version was tested for loading BLAST analysis on **proteins**.

Load BLAST subject records
---------------------------------
In case you did a BLAST against a multispecies protein database, like NCBI's nr or Uniprot's trembl or swissprot, you need to load previously all subject matches before loading the result itself. To do so, use the following command:

.. code-block:: bash

    python manage.py load_similarity_matches --file blast_result.xml --format blast-xml

* Loading this file can be faster if you increase the number of threads (--cpu).

Load BLAST
----------

If all queries and subjects are already loaded you can run the following command to load a BLAST xml result:

.. code-block:: bash

    python manage.py load_similarity --file blast_result.xml --format blast-xml --so_query polypeptide --so_subject protein_match --program diamond --programversion 0.9.24 --organism_query 'Oryza sativa' --organism_subject 'multispecies multispecies'

* Loading this file can be faster if you increase the number of threads (--cpu).

.. code-block:: bash

    python manage.py load_similarity --help

==================   ========================================================================================================
--file 		                        Blast XML file *
--format	                        blast-xml *
--so_query           Query Sequence Ontology term. (eg. assembly, mRNA, polypeptide) *
--so_subject         Subject Sequence Ontology term. (eg. protein_match if loading a BLAST result) *
--organism_query     Query's organism name. eg. 'Oryza sativa'. Cannot be 'multispecies' *
--organism_subject   Subject's organism name eg. 'Oryza sativa'. Put 'multispecies multispecies' if using a multispecies database. *
--program            Program *
--programversion     Program version *
--name               Name
--description        Description
--algorithm          Algorithm
--cpu 		     Number of threads
==================   ========================================================================================================

\* required fields


Remove file
-----------

If, by any reason, you need to remove a Blast result set you should use the command *remove_analysis*.

.. code-block:: bash

    python manage.py remove_analysis --help

* This command requires the analysis name (Analysis.sourcename)
