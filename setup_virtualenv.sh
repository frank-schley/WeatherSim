#!/usr/bin/env bash


if ! type virtualenv; then
    >&2 echo "ERROR: Could not find virtualenv of the user PATH"
    exit 1
fi

# Get the current directory of this script
# https://stackoverflow.com/questions/59895/getting-the-source-directory-of-a-bash-script-from-within
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
VIRTUALENV_DIR="${SCRIPT_DIR}/venv"

# Instantiate the virtual envronment
echo "Creating user virtual environment in the PROJECT_ROOT (${SCRIPT_DIR}) in directory called 'venv'"
virtualenv -p python3 "${VIRTUALENV_DIR}"

echo "Stepping in to virtual environment in order to install dependencies"
source "${VIRTUALENV_DIR}/bin/activate"
pip3 install -r "${SCRIPT_DIR}/requirements.txt"

echo "Virtualenv is ready..."
