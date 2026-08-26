# Models

This document describes how the [Django](https://www.djangoproject.com) `models.py` file for the [Chado](http://gmod.org/wiki/Chado_-_Getting_Started) schema was created. You **don't need** to create it again since machado already contains a copy of this file.

## Prerequisite

The list below contains the software and versions required by machado.

### PostgreSQL 9.5

Install PostgreSQL and create a database and user for loading the Chado schema. As the `postgres` user run:

```bash
psql
CREATE USER username WITH ENCRYPTED PASSWORD 'password';
CREATE DATABASE yourdatabase WITH OWNER username;
```

### Chado 1.31

Download the [Chado schema](https://downloads.sourceforge.net/project/gmod/gmod/chado-1.31/chado-1.31.tar.gz), unpack the file and load the `chado-1.31/schemas/1.31/default_schema.sql` to the database:

```bash
psql -h localhost -U username -W -d yourdatabase < chado-1.31/schemas/1.31/default_schema.sql
```

### Python 3.5.2

We strongly recommend creating a new virtualenv for your project:

```bash
virtualenv -p /usr/bin/python3 MYGENOME
cd MYGENOME
source bin/activate
```

### machado

Just grab the code using Git and install it:

```bash
git clone https://github.com/lmb-embrapa/machado.git src/machado
python src/machado/setup.py install
```

## The Django Project

Inside the `MYGENOME` directory, create a Django project with the following command:

```bash
django-admin startproject WEBPROJECT
cd WEBPROJECT
```

Then, configure the `WEBPROJECT/settings.py` file to connect to your Chado database:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'yourdatabase',
        'USER': 'username',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '',
    },
}
```

## The Model

Django has a command to generate a models file:

```bash
python manage.py inspectdb > unsortedmodels.py
```

This will create a raw `models.py` with a model for each table and view in the specified Postgres database. This file needs to be fixed as each foreign key relation should have a unique name in Django to support reverse relationships. The following Python code will create these unique names. The code rewrites the models and also generates an `admin.py` file:

```bash
fixChadoModel.py --input unsortedmodels.py
```

The resulting files, `models.py` and `admin.py`, are ready.

## References

- <http://gmod.org/wiki/Chado_Django_HOWTO>
