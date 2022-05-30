#!/bin/bash
# This is just a helper script to make releases for me easier (and to prevent I make a mistakes like the dummy I am).

if [ $# -eq 0 ]
  then
    echo "Usage: release.sh <version number>"
    exit 1
fi

BUILD_FILE=build/uAPI.mpy
if [[ ! -f "$BUILD_FILE" ]]; then
    echo "$BUILD_FILE not found"
    exit 1
fi

if [[ ! `git status --porcelain Changelog.md` ]]; then
    echo "No changes to Changelog.md made!"
    exit 1
fi

# CREATE A GITHUB RELEASE
echo $1 > VERSION
git add VERSION Changelog.md
git commit -m "Release Version $1"
git tag $1
git push
gh release create -F Changelog.md $1 build/uAPI.mpy

# RELEASE PYPI PACKAGE
wget https://raw.githubusercontent.com/pfalcon/pycopy-lib/master/sdist_upip.py
# delete old builds
rm -rf dist
python3 setup.py sdist
twine upload dist/*.tar.gz
