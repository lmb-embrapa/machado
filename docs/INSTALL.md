# machado

This repository contains information and tools to use the [Django](https://www.djangoproject.com) framework for accessing a [Chado](http://gmod.org/wiki/Chado_-_Getting_Started) database.

## Prerequisites

You may already have a populated Chado database and, therefore, are able to skip the PostgreSQL and Chado installation/configuration. The list bellow contains the softwares and versions used for the machado development.

#### PostgreSQL 9.5

Install PostgreSQL and create a database and user for loading the Chado schema.
As postgres user run:

    psql
    create user username with encrypted password 'password';
    create database yourdatabase with owner username;
    alter user username createdb;

#### Python 3.6

We strongly recommend creating a new virtualenv for your project

    virtualenv -p /usr/bin/python3.6 YOURPROJECT
    cd YOURPROJECT
    source bin/activate

### machado

Just grab the code using GIT and install it:

    git clone https://github.com/lmb-embrapa/machado.git src/machado
    python src/machado/setup.py install

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
            'NAME': 'yourdatabase',                                # Set the DB name
            'USER': 'username',                                    # Set the DB user
            'PASSWORD': 'password',                                # Set the DB password
            'HOST': 'localhost',                                   # Set the DB host
            'PORT': '',                                            # Set the DB port
        },
    }

### Let Django know about your machado

In the WEBPROJECT/settings.py file, add chado to INSTALLED_APPS section.

    INSTALLED_APPS = [
        ...
        'machado',
        'rest_framework',
        ...
    ]

(Follow instructions here: https://docs.djangoproject.com/en/1.10/intro/tutorial02/)


### List machado commands

    python manage.py

### Start you app and open the admin interface

You have to run the following command to create django admin tables:

    python manage.py migrate

Run tests to check the instalation:

    python manage.py test machado
    
And the following command to create an admin user:

    python manage.py createsuperuser

Now, just run the DJango server to access the admin interface:

    python manage.py runserver

The API interface will be available at http://localhost:8000/machado/api


## References

* http://gmod.org/wiki/Chado_Django_HOWTO
