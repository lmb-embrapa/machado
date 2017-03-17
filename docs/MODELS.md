# Django Chado

This document contains information and tools to create a [Django](https://www.djangoproject.com) models.py file for a [Chado](http://gmod.org/wiki/Chado_-_Getting_Started) database.

## Prerequisites

You may already have a populated Chado database and, therefore, are able to skip the PostgreSQL and Chado installation/configuration. The list bellow contains the softwares and versions used for the Django Chado development.

#### PostgreSQL 9.5

Install PostgreSQL and create a database and user for loading the Chado schema

#### Chado 3.1

Download [Chado](https://downloads.sourceforge.net/project/gmod/gmod/chado-1.31/chado-1.31.tar.gz), unpack the file and load the chado-1.31/schemas/1.31/default_schema.sql to the database

    psql YOURDATABASE < chado-1.31/schemas/1.31/default_schema.sql

#### Python 3.5.2

We strongly recommend creating a new virtualenv for your project

    python3 -m venv YOURPROJECT
    cd YOURPROJECT
    source bin/activate

#### Django 1.10.6

    pip install django

#### psycopg2 2.7.1

    pip install psycopg2

### DjangoChado

1. Download the package

        git clone https://azneto@bitbucket.org/azneto/django-chado.git


2. Install the package

        python setup.py install


## Preparations ##

From this point on it is assumed you have read the [Django introduction and tutorial](https://docs.djangoproject.com/en/1.10/intro) on the Django project website.

### Create a Django project
Inside YOURPROJECT directory create a Django project with the following command:

    django-admin startproject WEBPROJECT
    cd WEBPROJECT

Then, configure the WEBPROJECT/settings.py file to connect to your Chado database.

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',    # Set the DB driver
            'NAME': 'YOURDATABASE',                                # Set the DB name
            'USER': 'USERNAME',                                    # Set the DB user
            'PASSWORD': 'PASSWORD',                                # Set the DB password
            'HOST': 'localhost',                                   # Set the DB host
            'PORT': '',                                            # Set the DB port
        },
    }

### Create the Models

Django has a command to generate a Models file:

    python manage.py inspectdb > unsortedmodels.py

This will create a raw models.py with a model for each table and view in the specified Postgres database. This file needs to be fixed as each foreign key relation should have a unique name in Django to support reverse relationships. The following Python code will create these unique names. The code rewrites the models and also generate a admin.py file:

    fixChadoModel.py --input unsortedmodels.py

The resulting files, models.py and admin.py, are ready.



## References

* http://gmod.org/wiki/Chado_Django_HOWTO
