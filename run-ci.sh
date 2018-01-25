#!/usr/bin/env bash

set -e

TOX_ENV="${TOX_ENV:-ALL}"

# if we dont have a tag specified ignore "ALL"
if [ "${TOX_ENV}" != "ALL" ] || [ "${TRAVIS_TAG:-""}" != "" ]; then
    tox -e ${TOX_ENV}
else
    echo "Skipping tests for env=${TOX_ENV} tag=${TRAVIS_TAG}"
fi

# upload to code cov if specified
if [ ${RUN_CODECOV} == true ]; then
    codecov --flags "${TOX_ENV}"
else
    echo "Skipping codecov for env=${TOX_ENV} run_codecov=${RUN_CODECOV}"
fi
