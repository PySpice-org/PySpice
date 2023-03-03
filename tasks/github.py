####################################################################################################
#
# PySpice - A Spice package for Python
# Copyright (C) 2021 Fabrice Salvaire
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
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
