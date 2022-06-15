FROM python:3.10.4-slim

ENV POETRY_CACHE_DIR=/app/.poetry_cache \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_VIRTUALENVS_IN_PROJECT=false \
    PORT=80 \
    PYTHONPATH=/app/src:${PYTHONPATH} \
    SECRETS_DIR=/run/secrets


RUN apt-get update

RUN apt-get install --no-install-recommends --yes \
    bash \
    g++ \
    libffi-dev \
    libpq-dev \
    make \
    netcat \
    python3-dev

RUN apt-get clean && rm -rf /var/lib/apt/lists/* && rm -rf /var/cache/apt/archives

RUN useradd \
    --create-home \
    --shell /bin/bash \
    alpha

WORKDIR /app

COPY ./ ./

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

RUN install --owner alpha --directory "${SECRETS_DIR}"


USER alpha


EXPOSE $PORT


CMD ["make", "run-prod"]
