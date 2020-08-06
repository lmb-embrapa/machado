Installation
============

*machado* is a `Django <https://www.djangoproject.com/>`_ framework for `Chado <http://gmod.org/wiki/Chado_-_Getting_Started>`_.

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
    alter user username createdb;

Don't forget to configure the PostgreSQL server to allow regular users to connect (pg_hba.conf).

**Python 3.6**

Be sure to have the python development libraries installed (in Ubuntu 18.04, install with 'apt-get install python3-dev').

We strongly recommend creating a new virtualenv for your project

.. code-block:: bash

    virtualenv -p /usr/bin/python3.6 YOURPROJECT
    cd YOURPROJECT
    source bin/activate

**machado**

Just grab the code using GIT and install it:

.. code-block:: bash

    git clone https://github.com/lmb-embrapa/machado.git src/machado
    python src/machado/setup.py install

Preparation
-----------

From this point on it is assumed you have read the `Django introduction and tutorial <https://docs.djangoproject.com>`_ on the Django project website.

**Create a Django project**

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

**Let Django know about your machado**

In the WEBPROJECT/settings.py file, add chado to INSTALLED_APPS section.

.. code-block:: python

    INSTALLED_APPS = [
        ...
        'machado',
        'rest_framework',
        'drf_yasg',
        ...
    ]

(Additional information here: https://docs.djangoproject.com/en/2.1/intro/tutorial02/)

**List the machado commands**

.. code-block:: bash

    python manage.py

Start you app and open the admin interface
------------------------------------------

You have to run the following command to create django admin tables:

.. code-block:: bash

    python manage.py migrate

Run tests to check the instalation:

.. code-block:: bash

    python manage.py test machado

Now, just run the DJango server to access the web interface:

.. code-block:: bash

    python manage.py runserver

The API interface will be available at http://localhost:8000/machado/api


References
----------

* http://gmod.org/wiki/Chado_Django_HOWTO
