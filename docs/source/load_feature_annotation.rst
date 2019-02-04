Loading Feature Annotation Files
================================

Load Feature Annotation
-----------------------

.. code-block:: bash

    python manage.py load_feature_annotation --file feature_annotation.fa --organism 'Arabidopsis thaliana' --cvterm display

* Loading this file can be faster if you increase the number of threads (--cpu).

.. code-block:: bash

    python manage.py load_feature_annotation --help

=============   ==========================================================================================
--file 			Two-column tab separated file (feature.accession\tannotation text). *
--organism 		Species name (eg. Homo sapiens, Mus musculus) *
--cvterm 		cvterm.name from cv feature_property. (eg. display, note, product, alias, ontology_term) *
--cpu 			Number of threads
=============   ==========================================================================================

\* required fields


Remove Feature Annotation
-------------------------

If, by any reason, you need to remove a feature annotation you should use the command *remove_feature_annotation*.

.. code-block:: bash

    python manage.py remove_feature_annotation --help

