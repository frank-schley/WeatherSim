#!/usr/bin/env bash


if ! type virtualenv; then
    >&2 echo "ERROR: Could not find virtualenv of the user PATH"
    exit 1
fi
PYTHON_VERSION=$(python -c "import sys;t='{v[0]}.{v[1]}'.format(v=list(sys.version_info[:2]));sys.stdout.write(t)";)
if ! ( (echo "${PYTHON_VERSION}" | grep "2.7" >/dev/null) || (type -p python2) ); then
    echo "ERROR: Python2.7 does not seem to the system python, which is required by the project"
    exit 2
fi

# Get the current directory of this script
# https://stackoverflow.com/questions/59895/getting-the-source-directory-of-a-bash-script-from-within
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
VIRTUALENV_DIR="${SCRIPT_DIR}/venv"

# Instantiate the virtual envronment
echo "Creating user virtual environment in the PROJECT_ROOT (${SCRIPT_DIR}) in directory called 'venv'"
virtualenv --python="$(type -p python2)" "${VIRTUALENV_DIR}"

echo "Stepping in to virtual environment in order to install dependencies"
source "${VIRTUALENV_DIR}/bin/activate"
python -m pip install -r "${SCRIPT_DIR}/requirements.txt"

echo "Virtualenv is ready..."
