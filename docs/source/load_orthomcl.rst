Loading OrthoMCL results
========================

Load OrthoMCL
-------------

.. code-block:: bash

    python manage.py load_orthomcl --file groups.tx

* Loading this file can be faster if you increase the number of threads (--cpu).

.. code-block:: bash

    python manage.py load_orthomcl --help

=============   ==================================================================================
--file    		groups.txt file *
--cpu 			Number of threads
=============   ==================================================================================

\* output result from OrthoMCL software. Mandatory.


Remove orthology
----------------

If, by any reason, you need to remove orthology relationships, you should use the command *remove_feature_annotation --organism 'multispecies multispecies' --cvterm 'orthologous group'.* *

\*Every orthologous relations will be deleted.

.. code-block:: bash

    python manage.py remove_feature_annotation --help

====================  ========================================
--cvterm TERM          mandatory: 'orthologous group'
--organism ORGANISM    mandatory: 'multispecies multispecies'
====================  ========================================
