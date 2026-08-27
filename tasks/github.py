####################################################################################################
#
# PySpice - A Spice package for Python
# Copyright (C) 2021 Fabrice Salvaire
# SPDX-License-Identifier: AGPL-3.0-or-later
#
####################################################################################################

####################################################################################################

from invoke import task

try:
    from github import Github
except ImportError:
    pass

####################################################################################################

REPOSITORY_NAME = "FabriceSalvaire/PySpice"

####################################################################################################

def get_repo():
    g = Github()
    repo = g.get_repo(REPOSITORY_NAME)
    return repo

####################################################################################################

@task
def labels(ctx):
    repo = get_repo()
    labels = repo.get_labels()
    for label in labels:
        print(f'{label.name}: {label.description}')
