#!/bin/bash -ex

rm -rf build dist django_ormcache.egg-info

uv pip install -U setuptools wheel

uv build

uv publish
