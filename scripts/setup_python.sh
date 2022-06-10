#!/usr/bin/env bash

SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]:-$0}"; )" &> /dev/null && pwd 2> /dev/null; )";

py_required_version=$(cat "${SCRIPT_DIR}/../.python-version")
py_exists_version=$(python --version 2>/dev/null)
python_exists="$?"

which pyenv > /dev/null 2>&1
pyenv_exists="$?"


if [[ ${python_exists} = "0" ]]; then
  if [[ ${py_exists_version} = "${py_required_version}" ]]; then
    echo "Python ${py_required_version} is configured"
    exit 0
  else
    echo "Python ${py_required_version} is not installed and you have to deal with it on your own."
    exit 1
  fi
else
  if [[ ${pyenv_exists} = "0" ]]; then
    pyenv install "${py_required_version}"
    echo "Python ${py_required_version} is configured"
    exit 0
  else
    echo "Python ${py_required_version} is not installed and you have to deal with it on your own."
    exit 1
  fi
fi
