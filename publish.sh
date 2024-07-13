#!/bin/bash -ex

rm -rf build dist django_ormcache.egg-info

pip install -U setuptools wheel build

python -m build .

twine upload dist/*
