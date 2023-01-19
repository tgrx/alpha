# syntax=docker/dockerfile:1

ARG python_version
ARG version

FROM --platform=linux/amd64 python:${python_version}-slim

LABEL description="The template for building a web project."
LABEL org.opencontainers.image.authors="Alexander Sidorov <alexander@sidorov.dev>"
LABEL version=${version}


# ~~~~~~~~ System packages ~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

RUN apt update && apt upgrade --yes
RUN apt install --no-install-recommends --yes \
    bash \
    curl \
    g++ \
    libffi-dev \
    libpq-dev \
    make \
    netcat \
    python3-dev


# ~~~~~~~~ Poetry & Python dependencies ~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# forcing Poetry not to create venv
# and use "system" python for 3dp packages

ENV POETRY_HOME="/opt/poetry"
ENV PATH="${POETRY_HOME}/bin:${PATH}"
ENV POETRY_CACHE_DIR="${POETRY_HOME}/.cache"
ENV POETRY_VIRTUALENVS_ALWAYS_COPY=false
ENV POETRY_VIRTUALENVS_CREATE=false
ENV POETRY_VIRTUALENVS_IN_PROJECT=false
ENV POETRY_VIRTUALENVS_OPTIONS_SYSTEM_SITE_PACKAGES=true

# install Poetry

ARG poetry_version=1.3.2

RUN pip install "poetry==${poetry_version}"

# install 3dp packages to the system Python dist

WORKDIR "${POETRY_HOME}"

COPY pyproject.toml poetry.lock ./

ARG build

RUN if [ "${build}" = "dev" ]; \
    then \
        poetry install --with dev; \
    else \
        poetry install; \
    fi


# ~~~~~~~~ User & App directories ~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

ARG username=alpha
ARG user_id=1000
ARG group_id=1000

ARG dir_app="/app"

RUN addgroup --system --gid ${group_id} ${username} \
    && useradd -l --system --home-dir "/home/${username}" -u ${user_id} -g ${group_id} ${username} \
    && install --owner ${username} --group ${username} --directory "${dir_app}/.local/static/"

WORKDIR "${dir_app}"

USER ${username}

# test if fastapi is present
RUN python -c 'import httpx; print(httpx.__version__)'


# ~~~~~~~~ Health check ~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

ARG port

HEALTHCHECK --start-period=10s CMD curl -f http://localhost:${port}/livez/ || exit 1
