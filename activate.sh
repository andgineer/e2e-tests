#!/usr/bin/env bash
#
# "Set-ups or/and activates development environment"
#

VENV_FOLDER="venv"
PYTHON="python3.11"

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
    echo -e $CYAN"Creating virtual environment for python in ${VENV_FOLDER}"$NC
    if virtualenv ${VENV_FOLDER} --python=${PYTHON}; then
      echo -e $CYAN"creating VENV.."$NC
      python -m venv  ${VENV_FOLDER}
      . ${VENV_FOLDER}/bin/activate
      echo -e $CYAN"installing development dependencies.."$NC
      python -m pip install --upgrade pip
      python -m pip install -r requirements.txt
    else
      echo -e $RED"Error to create virtual env. Do you have virtualenv installed?"$NC
      return 1
    fi
else
    echo -e $CYAN"Activating virtual environment ..."$NC
    . ${VENV_FOLDER}/bin/activate
fi

if type conda 2>/dev/null; then
  echo -e $CYAN"deactivate conda for pure pip VENV.."$NC
  conda deactivate  # removing all stack if we activated conda for a number of times
  conda deactivate
  conda deactivate
fi

# ensure allure report dir exists
mkdir -p allure-results
