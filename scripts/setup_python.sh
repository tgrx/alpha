#!/usr/bin/env bash

if [[ ! "$(uname)" = "Darwin" ]]; then
  echo "only Mac OS X is currently supported"
  exit 1
fi

SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]:-$0}"; )" &> /dev/null && pwd 2> /dev/null; )";

version_required=$(cat "${SCRIPT_DIR}/../.python-version")
version_existing=$(python --version 2>/dev/null | sed -e 's/Python //g' || echo "0")

if [[ ! "${version_existing}" = "${version_required}" ]]; then
  which pyenv > /dev/null 2>&1
  pyenv_exists="$?"
  if [[ ! "${pyenv_exists}" = "0" ]]; then
    echo "Python ${version_required} is not installed and you have to deal with it on your own."
    exit 1
  fi
fi

pyenv install --skip-existing "${version_required}" || exit 1
echo "Python ${version_required} is configured"
