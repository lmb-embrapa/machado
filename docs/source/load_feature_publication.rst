Loading Feature Publication File
================================

Please notice the publications must be loaded in advance.
A feature can be linked to N publications.

Load Feature Publication
------------------------

.. code-block:: bash

    python manage.py load_feature_publication --file feature_publication.tab --organism 'Arabidopsis thaliana'

* Loading this file can be faster if you increase the number of threads (--cpu).

.. code-block:: bash

    python manage.py load_feature_publication --help

=============   ==========================================================================================
--file 			Two-column tab separated file (feature.accession<TAB>DOI). *
--organism 		Species name (eg. Homo sapiens, Mus musculus) *
--cpu 			Number of threads
=============   ==========================================================================================

\* required fields


Remove Feature Publication
--------------------------

If, by any reason, you need to remove a feature publication attribution, you should use the command *remove_publication*.

.. code-block:: bash

    python manage.py remove_publication --help

