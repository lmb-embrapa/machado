Loading OrthoMCL results
========================

Load OrthoMCL
-------------

.. code-block:: bash

    python manage.py load_orthomcl --file groups.txt

* Loading this file can be faster if you increase the number of threads (--cpu).

.. code-block:: bash

    python manage.py load_orthomcl --help

=============   ==================================================================================
--file    		Output result from OrthoMCL software.*
--cpu 			Number of threads
=============   ==================================================================================

\* required fields.


Remove orthology
----------------

If, by any reason, you need to remove orthology relationships, you should use the command *remove_feature_annotation*.

.. code-block:: bash

    python manage.py remove_feature_annotation --help

====================  ===============================================
--cvterm TERM         'orthologous group'*
--organism ORGANISM   Species name. (eg. Homo sapiens, Mus musculus)
====================  ===============================================

\* required fields
