#!/usr/bin/env bash
set -Eeuxo pipefail

# pyenv installer (for macOS)
# updated: 2020-09-05

# use the following to enable diagnostics
# export PYENV_DIAGNOSE=1

if [[ "$(uname)" == "Darwin" ]]; then
  if [ -n "${DIAGNOSE_PYENV-}" ] ; then
    pyenv install --list
  fi
  if ! [[ ${TRAVIS_PYTHON_VERSION} =~ .*-dev$ ]] ; then
    TRAVIS_PYTHON_VERSION="$(pyenv install --list | grep -E " ${TRAVIS_PYTHON_VERSION}(\.[0-9brc]+)+" | tail -n 1 | sed -e 's/^[[:space:]]*//')"
  fi
  pyenv install "${TRAVIS_PYTHON_VERSION}"
  pyenv global "${TRAVIS_PYTHON_VERSION}"
  echo -e 'if command -v pyenv 1>/dev/null 2>&1; then\n  eval "$(pyenv init -)"\nfi' >> ~/.bash_profile
fi
