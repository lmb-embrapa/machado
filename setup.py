"""Setup."""


import os

from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), "README.md")) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name="machado",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    license="BSD License",
    description="machado is a Django app that contains tools to interact "
    "with a Chado database.",
    long_description=README,
    url="https://bitbucket.org/azneto/djangochado",
    author="Adhemar",
    author_email="azneto@gmail.com",
    classifiers=[
        "Environment :: Command Line",
        "Framework :: Django",
        "Programming Language :: Python" "Programming Language :: Python :: 3",
    ],
    scripts=["bin/fixChadoModel.py"],
    install_requires=[
        "django==2.2.9",
        "psycopg2-binary==2.8.2",
        "biopython==1.73",
        "obonet==0.2.5",
        "tqdm==4.31.1",
        "typing==3.6.6",
        "bibtexparser==1.1.0",
        "djangorestframework==3.11.0",
        "drf-nested-routers==0.91",
        "coreapi==2.3.3",
        "django-cors-headers==3.0.1",
        "pysam==0.15.2"
    ],
    zip_safe=False,
)
