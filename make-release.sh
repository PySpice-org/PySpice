####################################################################################################
#
# Make a Release
#
####################################################################################################

# Set the environment
. setenv.sh

# Cleanup the repository
./tools/clean

# Check licence
./tools/check-license

# Make Source Tar Archive
python setup.py sdist

# Build
python setup.py bdist
python setup.py bdist_rpm
# python setup.py upload

# Check file list in archive
./tools/check-for-missing-files

# Test RPM

####################################################################################################
#
# End
#
####################################################################################################
