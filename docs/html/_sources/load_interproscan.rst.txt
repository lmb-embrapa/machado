Loading InterproScan results
============================

In order to load an InterproScan results file, both the query and the subject records must be previously stored.
The current version was tested for loading InterproScan analysis on **proteins**.

Load InterproScan subject records
---------------------------------

.. code-block:: bash

    python manage.py load_similarity_matches --file interproscan_result.xml --format interproscan-xml

* Loading this file can be faster if you increase the number of threads (--cpu).

Load InterproScan similarity
----------------------------

.. code-block:: bash

    python manage.py load_similarity --file interproscan_result.xml --format interproscan-xml --so_query polypeptide --so_subject protein_match --program interproscan --programversion 5 --organism_query 'Oryza sativa' --organism_subject 'multispecies multispecies'

* Loading this file can be faster if you increase the number of threads (--cpu).

.. code-block:: bash

    python manage.py load_similarity --help

==================   ========================================================================================================
--file 		     InterproScan XML file *
--format	     interproscan-xml *
--so_query           Query Sequence Ontology term. (polypeptide) *
--so_subject         Subject Sequence Ontology term. (protein_match) *
--organism_query     Query's organism name. eg. 'Oryza sativa'. Cannot be 'multispecies'. *
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

If, by any reason, you need to remove an InterproScan result set you should use the command *remove_analysis*.

.. code-block:: bash

    python manage.py remove_analysis --help

* This command requires the analysis name (Analysis.sourcename)
