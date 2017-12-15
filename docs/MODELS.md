# Django Chado

This document contains information and tools to create a [Django](https://www.djangoproject.com) models.py file for a [Chado](http://gmod.org/wiki/Chado_-_Getting_Started) database.

## Prerequisites

You may already have a populated Chado database and, therefore, are able to skip the PostgreSQL and Chado installation/configuration. The list bellow contains the softwares and versions used for the Django Chado development.

#### PostgreSQL 9.5

Install PostgreSQL and create a database and user for loading the Chado schema.
As postgres user run:

    psql
    create user username with encrypted password 'password';
    create database yourdatabase with owner username;

#### Chado 1.31

Download [Chado](https://downloads.sourceforge.net/project/gmod/gmod/chado-1.31/chado-1.31.tar.gz), unpack the file and load the chado-1.31/schemas/1.31/default_schema.sql to the database

    psql -h localhost -U username -W -d yourdatabase < chado-1.31/schemas/1.31/default_schema.sql

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

Just grab the code using GIT and install it:

    git clone https://bitbucket.org/azneto/django-chado.git src/django-chado
    python src/django-chado/setup.py install

### Create a Django project
Inside YOURPROJECT directory create a Django project with the following command:

    django-admin startproject WEBPROJECT
    cd WEBPROJECT

Then, configure the WEBPROJECT/settings.py file to connect to your Chado database.

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

### Create the Models

Django has a command to generate a Models file:

    python manage.py inspectdb > unsortedmodels.py

This will create a raw models.py with a model for each table and view in the specified Postgres database. This file needs to be fixed as each foreign key relation should have a unique name in Django to support reverse relationships. The following Python code will create these unique names. The code rewrites the models and also generate a admin.py file:

    fixChadoModel.py --input unsortedmodels.py

The resulting files, models.py and admin.py, are ready.



## References

* http://gmod.org/wiki/Chado_Django_HOWTO
