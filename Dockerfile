ARG PYTHON_VERSION="3.13"

FROM python:${PYTHON_VERSION}

SHELL ["/bin/bash", "-c"]

# set timezone

ARG TIMEZONE="Europe/Warsaw"

RUN set -Eeuxo pipefail && \
  apt-get update && \
  apt-get install --no-install-recommends -y \
    tzdata && \
  echo "${TIMEZONE}" > /etc/timezone && \
  cp "/usr/share/zoneinfo/${TIMEZONE}" /etc/localtime && \
  apt-get -qy autoremove && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/*

# add a non-root user

ARG USER_ID=1000
ARG GROUP_ID=1000
ARG AUX_GROUP_IDS=""

RUN set -Eeuxo pipefail && \
  (addgroup --gid "${GROUP_ID}" user || echo "group ${GROUP_ID} already exists, so not adding it") && \
  adduser --disabled-password --gecos "User" --uid "${USER_ID}" --gid "${GROUP_ID}" user && \
  echo ${AUX_GROUP_IDS} | xargs -n1 echo | xargs -I% addgroup --gid % group% && \
  echo ${AUX_GROUP_IDS} | xargs -n1 echo | xargs -I% usermod --append --groups group% user

# install dependencies

RUN set -Eeuxo pipefail && \
  apt-get update && \
  apt-get install --no-install-recommends -y \
    git && \
  apt-get -qy autoremove && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/*

WORKDIR /home/user/version-query

COPY --chown=${USER_ID}:${GROUP_ID} requirements*.txt ./

RUN set -Eeuxo pipefail && \
  pip3 install --no-cache-dir -r requirements_ci.txt

# prepare version-query for testing

USER user

WORKDIR /home/user

ENV EXAMPLE_PROJECTS_PATH="/home/user"

RUN set -Eeuxo pipefail && \
  git clone https://github.com/PyCQA/pycodestyle pycodestyle && \
  cd pycodestyle && \
  python setup.py build && \
  cd - && \
  git clone https://github.com/mbdevpl/argunparse argunparse && \
  cd argunparse && \
  pip install -r requirements_test.txt && \
  python setup.py build && \
  cd - && \
  git clone https://github.com/python-semver/python-semver semver && \
  cd semver && \
  python -m build && \
  cd - && \
  pip install jupyter  # example package that uses metadata.json

WORKDIR /home/user/version-query

VOLUME ["/home/user/version-query"]
