JBrowse (optional)
==================


The `JBrowse <https://jbrowse.org>`_ software renders genomic tracks from Chado using the *machado* API.


**JBrowse**

Install JBrowse following the `official instructions <https://jbrowse.org/docs/installation.html>`_.

The *machado* source contains the directory extras. Copy the file extras/trackList.json.sample to the JBrowse data directory, inside a subdirectory with the name of the organism (eg. /var/www/html/jbrowse/data/Arabidopsis thaliana) and rename it to trackList.json
This directory structure will enable machado to embed JBrowse in its pages.

.. code-block:: bash

    mkdir -p "/var/www/html/jbrowse/data/Arabidopsis thaliana"
    cp extras/trackList.json.sample "/var/www/html/jbrowse/data/Arabidopsis thaliana/trackList.json"

Edit the file to set the **organism** name you have loaded to the database.


**machado API**

Start the *machado* API framework:

.. code-block:: bash

    python manage.py runserver


Once the server is running, just go to your browser and open your JBrowse instance (eg. http://localhost/jbrowse/?data=data/Arabidopsis thaliana)


**machado**

The settings.py file should contain these variables

.. code-block:: bash

   MACHADO_JBROWSE_URL = 'http://localhost/jbrowse'
   MACHADO_JBROWSE_OFFSET = 1200

MACHADO_JBROWSE_URL: contains the base URL to the JBrowse instalation. The URL must contain the protocol (i.e. http or https)

MACHADO_OFFSET: the number of bp upstream and downstream of the feature.


