# Django Chado

This repository contains information and tools to use the [Django](https://www.djangoproject.com) framework for accessing a [Chado](http://gmod.org/wiki/Chado_-_Getting_Started) database.

## Prerequisites

You may already have a populated Chado database and, therefore, are able to skip the PostgreSQL and Chado installation/configuration. The list bellow contains the softwares and versions used for the Django Chado development.

#### PostgreSQL 9.5

Install PostgreSQL and create a database and user for loading the Chado schema.
As postgres user run:

    psql
    create user username with encrypted password 'password';
    create database yourdatabase with owner username;
    grant all privileges on database yourdatabase to username;

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

#### biopython 1.69

    pip install biopython

#### pysam 0.11.2.1

    pip install pysam

#### obonet 0.2.1

    pip install obonet

### DjangoChado

Just grab the code using GIT and install it:

    git clone https://bitbucket.org/azneto/django-chado.git src/django-chado
    python src/django-chado/setup.py install

## Preparations ##

From this point on it is assumed you have read the [Django introduction and tutorial](https://docs.djangoproject.com/en/1.10/intro) on the Django project website.

#### Create a Django project
Inside YOURPROJECT directory create a Django project with the following command:

    django-admin startproject WEBPROJECT
    cd WEBPROJECT

Then, configure the WEBPROJECT/settings.py file to connect to your Chado database.

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',    # Set the DB driver
            'NAME': 'yourdatabase',                                # Set the DB name
            'USER': 'username',                                    # Set the DB user
            'password': 'password',                                # Set the DB password
            'HOST': 'localhost',                                   # Set the DB host
            'PORT': '',                                            # Set the DB port
        },
    }

### Let Django know about your django-chado

In the WEBPROJECT/settings.py file, add chado to INSTALLED_APPS section.

    INSTALLED_APPS = [
        ...
        'chado',
    ]

(Follow instructions here: https://docs.djangoproject.com/en/1.10/intro/tutorial02/)

### List django-chado commands

    python manage.py

### Start you app and open the admin interface

You have to run the following command to create django admin tables:

    python manage.py migrate

And the following command to create an admin user:

    python manage.py createsuperuser

Now, just run the DJango server to access the admin interface:

    python manage.py runserver

The webapp admin interface will be available at http://localhost:8000/admin

