#!/usr/bin/env python

import os
import sys

from setuptools import setup


if sys.argv[-1] == "publish":
    os.system("python setup.py register sdist bdist_wheel upload")
    sys.exit()


readme_text = open("README.rst", "r").read()

setup(
    name="django-ormcache",
    version="1.2.1",
    description="ORM cache for Django",
    license="MIT",
    keywords="cache django",
    author="Corey Farwell",
    author_email="coreyf@rwell.org",
    maintainer="Educreations Engineering",
    maintainer_email="engineering@educreations.com",
    url="https://github.com/educreations/django-ormcache",
    long_description=readme_text,
    packages=["ormcache"],
    package_dir={"ormcache": "ormcache"},
    install_requires=["Django>=1.9,<4.0"],
    classifiers=[
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development",
    ],
)
