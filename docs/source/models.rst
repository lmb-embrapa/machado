Models
======

This document describes how the `Django <https://www.djangoproject.com>`_ models.py file for the `Chado <http://gmod.org/wiki/Chado_-_Getting_Started>`_ schema was created. You **don't need** to create it again since *machado* already contains a copy of this file.

Prerequisite
------------

The list bellow contains the softwares and versions required by *machado*.

**PostgreSQL 9.5**

Install PostgreSQL and create a database and user for loading the Chado schema.
As postgres user run:

.. code-block:: bash

    psql
    create user username with encrypted password 'password';
    create database yourdatabase with owner username;

**Chado 1.31**

Download `Chado schema <https://downloads.sourceforge.net/project/gmod/gmod/chado-1.31/chado-1.31.tar.gz>`_, unpack the file and load the chado-1.31/schemas/1.31/default_schema.sql to the database.

.. code-block:: bash

    psql -h localhost -U username -W -d yourdatabase < chado-1.31/schemas/1.31/default_schema.sql

**Python 3.5.2**

We strongly recommend creating a new virtualenv for your project

.. code-block:: bash

    virtualenv -p /usr/bin/python3 YOURPROJECT
    cd YOURPROJECT
    source bin/activate

**machado**

Just grab the code using GIT and install it:

.. code-block:: bash

    git clone https://github.com/lmb-embrapa/machado.git src/machado
    python src/machado/setup.py install

The Django project
------------------

Inside YOURPROJECT directory create a Django project with the following command:

.. code-block:: bash

    django-admin startproject WEBPROJECT
    cd WEBPROJECT

Then, configure the WEBPROJECT/settings.py file to connect to your Chado database.

.. code-block:: python

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',    # Set the DB driver
            'NAME': 'yourdatabase',                                # Set the DB name
            'USER': 'username',                                    # Set the DB user
            'PASSWORD': 'password',                                # Set the DB password
            'HOST': 'localhost',                                   # Set the DB host
            'PORT': '',                                            # Set the DB port
        },
    }

The model
---------

Django has a command to generate a Models file:

.. code-block:: python

    python manage.py inspectdb > unsortedmodels.py

This will create a raw models.py with a model for each table and view in the specified Postgres database. This file needs to be fixed as each foreign key relation should have a unique name in Django to support reverse relationships. The following Python code will create these unique names. The code rewrites the models and also generate a admin.py file:

.. code-block:: bash

    fixChadoModel.py --input unsortedmodels.py

The resulting files, models.py and admin.py, are ready.

References
----------

* http://gmod.org/wiki/Chado_Django_HOWTO
