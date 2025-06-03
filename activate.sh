#!/usr/bin/env bash
#
# "Set-ups or/and activates development environment"
#

VENV_FOLDER=".venv"
PRIMARY_PYTHON_VERSION="3.13"  # sync with .github/workflows/docs.yml&static.yml

RED='\033[1;31m'
GREEN='\033[1;32m'
CYAN='\033[1;36m'
NC='\033[0m' # No Color

if ! (return 0 2>/dev/null) ; then
    # If return is used in the top-level scope of a non-sourced script,
    # an error message is emitted, and the exit code is set to 1
    echo
    echo -e $RED"This script should be sourced like"$NC
    echo "    . ./activate.sh"
    echo
    exit 1
fi

# virtual env
if [[ ! -d ${VENV_FOLDER} ]] ; then
    unset CONDA_PREFIX  # if conda is installed, it will mess with the virtual env

    echo -e $CYAN"Creating virtual environment for python in ${VENV_FOLDER}"$NC
    if uv venv ${VENV_FOLDER} --python=python${PRIMARY_PYTHON_VERSION}; then
      START_TIME=$(date +%s)

      . ${VENV_FOLDER}/bin/activate
      uv pip install --upgrade pip
      uv pip install -r requirements.txt

      END_TIME=$(date +%s)
      echo "Environment created in $((END_TIME - $START_TIME)) seconds"
    else
      echo -e $RED"Error to create virtual env. Do you have Astral's UV installed ( https://github.com/astral-sh/uv )?"$NC
      return 1
    fi
else
    echo -e $CYAN"Activating virtual environment ..."$NC
    . ${VENV_FOLDER}/bin/activate
fi

# ensure allure report dir exists
mkdir -p allure-results