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

If, by any reason, you need to remove orthology relationships, you should use the command *remove_relationship --file*. **Every orthologous relations from file (e.g. 'groups.txt' from OrthoMCL) will be deleted on cascade**.

.. code-block:: bash

    python manage.py remove_relationship --help

* This command requires the file name 'groups.txt' used before as input to load orthologies.
