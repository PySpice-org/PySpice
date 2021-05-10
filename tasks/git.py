####################################################################################################
#
# PySpice - A Spice package for Python
# Copyright (C) 2019 Fabrice Salvaire
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

import datetime
fromtimestamp = datetime.datetime.fromtimestamp

from invoke import task
# import sys

try:
    import pygit2 as git
except ImportError:
    git = None

####################################################################################################

@task
def push_tags(ctx):
    # git push --delete origin v1.4.3_beta0
    # git tag -d v1.4.3_beta0
    ctx.run('git push --tags')

####################################################################################################

@task
def uncommit(ctx):
    ctx.run('git reset --soft HEAD~')

####################################################################################################

@task
def get_commits(ctx):

    path = '.'
    repository_path = git.discover_repository(path)
    # print(repository_path)
    repository = git.Repository(repository_path)

    head = repository.head
    head_commit = repository[head.target]

    # GIT_SORT_TOPOLOGICAL. Sort the repository contents in topological order (parents before children);
    # this sorting mode can be combined with time sorting.
    sorting = git.GIT_SORT_TOPOLOGICAL   # git.GIT_SORT_TIME
    commits = [commit for commit in repository.walk(head_commit.id, sorting)]   # Fixme:

    template = '''
====================================================================================================
{message}

  -------------------------------------------------
  {name} <{email}> / {timestamp}
  {id}
'''

    for commit in commits:
        fields = {
            'message': commit.message.strip(),
            'id': commit.hex,
            'timestamp': fromtimestamp(commit.commit_time).strftime('%Y-%m-%d %H:%M:%S'),
            'name': commit.committer.name,   # author
            'email': commit.committer.email,
        }
        if 'salvaire' not in fields['name'].lower():
            print(template.lstrip().format(**fields))

####################################################################################################

@task
def fetch_pr(ctx, pr_id):
    # https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/checking-out-pull-requests-locally
    branch_name = f'pr/{pr_id}'
    ctx.run(f'git fetch origin pull/{pr_id}/head:{branch_name}')
    # git checkout {branch_name}
    # rework ...
    # git push origin {branch_name}
    # -> create new PR

# @task
# def fetch_pr_range(ctx, start_id, stop_id):
#     for i in range(int(start_id), int(stop_id+1)):
#         ctx.run('git fetch origin pull/{0}/head:pr/{0}'.format(i))

####################################################################################################

#  https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/merging-a-pull-request
