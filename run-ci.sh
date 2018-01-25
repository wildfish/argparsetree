#!/usr/bin/env bash

set -e

TOX_ENV=$(echo py$TRAVIS_PYTHON_VERSION | tr -d .)

if [ -n "${TRAVIS_TAG}" ]; then
    PACKAGE_VERSION=`grep -oP '[0-9]+\.[0-9]+\.[0-9]+' argparsetree/__init__.py`

    if [ "${TRAVIS_TAG}" != "${PACKAGE_VERSION}" ]; then
        echo "Tag version (${TRAVIS_TAG}) is not equal to the package tag (${PACKAGE_VERSION})"
        exit 1
    fi
fi

tox -e flake -e ${TOX_ENV}
codecov --flags "${TOX_ENV}"
