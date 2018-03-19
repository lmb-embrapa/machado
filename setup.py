"""Setup."""


import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-chado',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    license='BSD License',
    description='DjangoChado is a Django app that contains tools to interact '
                'with a Chado database.',
    long_description=README,
    url='https://bitbucket.org/azneto/djangochado',
    author='Adhemar',
    author_email='azneto@gmail.com',
    classifiers=[
        'Environment :: Command Line',
        'Framework :: Django',
        'Programming Language :: Python'
        'Programming Language :: Python :: 3'
    ],
    scripts=[
        'bin/fixChadoModel.py'
    ],
    install_requires=[
        'django>=2.0.1',
        'psycopg2>=2.7.3.2',
        'biopython>=1.70',
        'pysam>=0.13',
        'obonet>=0.2.2',
        'tqdm>=4.19.5',
        'typing>=3.6.4',
        'bibtexparser>=1.0.1',
        'django-rest-framework>=0.1.0',
        'drf-nested-routers>-0.90.2',
        'coreapi>=2.3.3',
    ],
    zip_safe=False,
)
