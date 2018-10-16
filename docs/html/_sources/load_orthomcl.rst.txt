Loading OrthoMCL results
========================

Load OrthoMCL
-------------

.. code-block:: bash

    python manage.py load_orthomcl --filename groups.txt

* Loading this file can be faster if you increase the number of threads (--cpu).

.. code-block:: bash

    python manage.py load_orthomcl --help

=============   ==================================================================================
--filename 		groups.txt file *
--cpu 			Number of threads
=============   ==================================================================================

\* output result from OrthoMCL software. Mandatory.


Remove orthology
----------------

TODO - If, by any reason, you need to remove orthology relationships, you should use the command *remove_orthology --filename*. **Every orthologous relations from filename will be deleted on cascade**.

.. code-block:: bash

    python manage.py remove_orthology --help

* This command requires the file name 'groups.txt' used before as input to load orthologies.
