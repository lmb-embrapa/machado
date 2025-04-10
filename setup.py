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
        "django~=5.1.1",
        "psycopg2-binary~=2.9.9",
        "networkx~=3.3",
        "obonet~=1.1.0",
        "biopython~=1.84",
        "tqdm~=4.66.5",
        "typing~=3.7.4.3",
        "bibtexparser~=1.4.1",
        "djangorestframework~=3.15.2",
        "drf-yasg==1.21.8",
        "drf-nested-routers~=0.94.1",
        "pysam~=0.22.1",
        "django-haystack~=3.3.0",
        "setuptools~=76.0.0",
        "python-decouple~=3.8",
        "elasticsearch >=7,<8",
        "django-cors-headers~=4.7.0",
    ],
    zip_safe=False,
)
