#!/bin/bash
# https://github.com/AnacondaRecipes/conda-feedstock/blob/master/recipe/build.sh

# --record                             filename in which to record list of
#                                      installed files
# --single-version-externally-managed  used by system package builders to
#                                      create 'flat' eggs

invoke release.update-git-sha
$PYTHON setup.py install --single-version-externally-managed --record record.txt
