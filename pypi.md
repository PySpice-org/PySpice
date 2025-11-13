# Distributing this package
Source: https://packaging.python.org/tutorials/packaging-projects/

### Edit setup.py

Make sure you refer to setuptools:

	from setuptools import setup

### Edit the package version

/PySpice/__init__.py to change the version.

### Generating distribution archives

Make sure you have the latest versions of setuptools and wheel installed:

`python -m pip install --upgrade setuptools wheel`

Install twine to upload the distribution packages. You’ll need to install Twine:

`python -m pip install --upgrade twine`

### Uploading

Make sure you setup the package version correctly in `setup.py` as this cannot be reverted.

Cleanup:

rm -rf build dist *.egg-info

Build the distribution:

`python setup.py sdist bdist_wheel`

Run Twine to upload all of the archives:

`python -m twine upload dist/*`

### Get version of package

pip show <package>