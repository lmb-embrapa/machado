"""Setup."""


import os

from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), "README.md")) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name="machado",
    version="0.5.0",
    packages=find_packages(),
    include_package_data=True,
    license="GPL License",
    description="This library provides users with a framework to store, search and visualize biological data.",
    long_description=README,
    url="https://github.com/lmb-embrapa/machado",
    author="LMB",
    author_email="",
    classifiers=[
        "Environment :: Console",
        "Framework :: Django :: 3.2",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
    ],
    scripts=["bin/fixChadoModel.py"],
    install_requires=[
        "django~=4.1.6",
        "psycopg2-binary~=2.9.5",
        "networkx~=2.8.8",
        "obonet~=0.3.1",
        "biopython~=1.80",
        "tqdm~=4.64.1",
        "typing~=3.7.4.3",
        "bibtexparser~=1.4.0",
        "djangorestframework~=3.14.0",
        "drf-yasg==1.21.4",
        "drf-nested-routers~=0.93.4",
        "pysam~=0.20.0",
        "django-haystack~=3.2.1",
    ],
    zip_safe=False,
)
