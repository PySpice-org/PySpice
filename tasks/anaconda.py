####################################################################################################
#
# PySpice - A Spice package for Python
# Copyright (C) 2020 Fabrice Salvaire
# SPDX-License-Identifier: AGPL-3.0-or-later
#
####################################################################################################

####################################################################################################

from pathlib import Path
import shutil

from invoke import task

####################################################################################################

# https://github.com/conda-forge/pyspice-feedstock

# enable anaconda environment
#   source .../miniconda3/bin/activate

@task()
def conda_build(ctx):
    with ctx.cd('anaconda'):
        ctx.run('conda build .')
        # ctx.run('conda build purge')

@task()
def conda_login(ctx):
    path = Path(__file__).parent.joinpath('anaconda-login.txt')
    with open(path) as fh:
        username = fh.readline().strip()
        password = fh.readline().strip()
    print('"{}" "{}"'.format(username, password))
    ctx.run('anaconda login --username="{}" --password="{}"'.format(username, password))

@task(conda_build, conda_login)
def conda_upload(ctx):
    result = ctx.run('conda build . --output')
    path = str(result.stdout).strip()
    ctx.run('anaconda upload {}'.format(path))
