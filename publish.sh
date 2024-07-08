#!/bin/bash -ex

pip install -U setuptools wheel build

python -m build .

twine upload dist/*
