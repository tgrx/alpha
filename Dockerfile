# syntax=docker/dockerfile:1

ARG python_version
ARG version

FROM --platform=linux/amd64 python:${python_version}-slim

LABEL description="The template for building a web project."
LABEL org.opencontainers.image.authors="Alexander Sidorov <alexander@sidorov.dev>"
LABEL version=${version}

ENV POETRY_CACHE_DIR=/app/.poetry_cache \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_VIRTUALENVS_IN_PROJECT=false \
    PORT=${PORT:-80} \
    PYTHONPATH=/app/src:${PYTHONPATH} \
    SECRETS_DIR=/run/secrets


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

RUN apt clean && rm -rf /var/lib/apt/lists/* && rm -rf /var/cache/apt/archives

WORKDIR /app

COPY poetry.toml poetry.lock pyproject.toml .env ./

RUN pip install --no-cache pipx

RUN pipx install \
    poetry

RUN pipx run poetry export \
    --dev \
    --format=requirements.txt \
    --output=/app/requirements.txt \
    --without-hashes

RUN pip install \
    --no-cache-dir \
    --requirement /app/requirements.txt

COPY ./ ./

RUN useradd \
    --create-home \
    --shell /bin/bash \
    alpha

RUN install --owner alpha --directory "${SECRETS_DIR}"

USER alpha

EXPOSE ${PORT}

CMD ["make", "run-prod"]

HEALTHCHECK --start-period=10s CMD curl -f http://localhost:${PORT}/ || exit 1
