JBrowse (optional)
==================


The `JBrowse <https://jbrowse.org>`_ software renders genomic tracks from Chado using the *machado* API.


**JBrowse**

Before installing Jbrowse you should probably have Bioperl installed in your system (tested in Ubuntu 18.04):

.. code-block:: bash

    sudo apt install bioperl

Then install JBrowse following the `official instructions <https://jbrowse.org/docs/installation.html>`_:

In Ubuntu 18.04:

Install some prerequisites:

 .. code-block:: bash

    sudo apt install build-essential zlib1g-dev curl

Also *Node.js* is needed:

.. code-block:: bash

    curl -sL https://deb.nodesource.com/setup_11.x | sudo -E bash -
    sudo apt-get install -y nodejs

Finally, proceed with JBrowse installation

.. code-block:: bash

   wget https://github.com/GMOD/jbrowse/releases/download/1.16.2-release/JBrowse-1.16.2.zip
   unzip JBrowse-1.16.2.zip
   sudo mv JBrowse-1.16.2 /var/www/html/jbrowse
   cd /var/www/html
   sudo chown `whoami` jbrowse
   cd jbrowse
   ./setup.sh # don't do sudo ./setup.sh

**configuring JBrowse**

The *machado* source contains the directory extras. Copy the file extras/trackList.json.sample to the JBrowse data directory, inside a subdirectory with the name of the organism (e.g. /var/www/html/jbrowse/data/Arabidopsis thaliana) and rename it to trackList.json
This directory structure will enable machado to embed JBrowse in its pages.

.. code-block:: bash

    mkdir -p "/var/www/html/jbrowse/data/Arabidopsis thaliana"
    cp extras/trackList.json.sample "/var/www/html/jbrowse/data/Arabidopsis thaliana/trackList.json"

Edit the file trackList.json to set the **organism** name you have loaded to the database.

**In case you have WSGI apache module configured and running**, change the *baseUrl* variable in trackList.json to refer to the proper address:

.. code-block:: bash

    baseUrl":    "http://localhost/YOURPROJECT/api/jbrowse"

* Now repeat the steps above for as many other organisms as you may have loaded to the database.

* Remember to restart the Apache server after the modifications.


**machado API**

**In case you don't have the WSGI module installed under Apache** (and did change the *baseUrl* variable in trackList.json), start the *machado* API framework:

.. code-block:: bash

    python manage.py runserver


Once the server is running, just go to your browser and open your JBrowse instance (e.g.: `<http://localhost/jbrowse/?data=data/Arabidopsis\ thaliana>`_ ).


**machado**

The settings.py file should contain these variables

.. code-block:: bash

   MACHADO_JBROWSE_URL = 'http://localhost/jbrowse'

   MACHADO_JBROWSE_TRACKS = 'ref_seq,gene,transcripts,CDS,SNV'

   MACHADO_JBROWSE_OFFSET = 1200

MACHADO_JBROWSE_URL: the base URL to the JBrowse instalation. The URL must contain the protocol (i.e. http or https)

MACHADO_JBROWSE_TRACKS: the name of the tracks to be displayed ('ref_seq,gene,transcripts,CDS,SNV' if not set).

MACHADO_OFFSET: the number of bp upstream and downstream of the feature (1000 if not set).

Use reference from FASTA file
-----------------------------

If the reference sequences are really long (>200Mbp), there may be memory issues during the loading process and JBrowse may take too long to render the tracks. To avoid this, follow instructions to create and use and indexed fasta file as source the reference sequences `<https://jbrowse.org/docs/tutorial.html>`_.

Follow the steps below.

Put the genome's assembly fasta file into your jbrowse organism's 'data/seq' directory (for example: /var/www/html/jbrowse/data/'Glycine max'/data/seq/Gmax.fa), change to this directory, and run the command:

.. code-block:: bash

    samtools faidx Gmax.fa

* A 'Gmax.fa.fai' indexed fasta file will be created.


Now, modify your default trackList.json file. You need to make two modifications, first replace the "refSeqs" entry line (probably the second line of the file) with the following line:

.. code-block:: bash

    "refSeqs" : "data/seq/Gmax.fa.fai",

And then change a whole code chunk, as follows:

.. code-block:: bash

    {
     "category" : "1. Reference sequence",
     "faiUrlTemplate" : "data/seq/Gmax.fa.fai",
     "key" : "Reference sequence",
     "label" : "ref_seq",
     "seqType" : "dna",
     "storeClass" : "JBrowse/Store/SeqFeature/IndexedFasta",
     "type" : "SequenceTrack",
     "urlTemplate" : "data/seq/Gmax.fa",
     "useAsRefSeqStore" : 1
    }

* The code above should replace all code from the "1. Referece sequence" category track code chunk.
* make sure "urlTemplate" points to the fasta file path, not the .fai indexed one.

Now restart the apache daemon for changes to take effect.

.. code-block:: bash

    systemctl restart apache2
