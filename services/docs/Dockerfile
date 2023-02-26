# syntax=docker/dockerfile:1

# ==============================================
# ~~~~~~~~ Stage 0: Task ~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


FROM golang:bullseye@sha256:a0b51fe882f269828b63e7f69e6925f85afc548cf7cf967ecbfbcce6afe6f235 AS build-task
ENV GOBIN=/app/bin
WORKDIR /app
RUN go install github.com/go-task/task/v3/cmd/task@latest


# ==============================================
# ~~~~~~~~ Stage 1: docs ~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

FROM squidfunk/mkdocs-material:9.0.13
LABEL description="Alpha :: Docs"
LABEL org.opencontainers.image.authors="Alexander Sidorov <alexander@sidorov.dev>"

COPY --from=build-task /app/bin/task /usr/bin/task

ARG VERSION=dev
LABEL version=${VERSION}

# ~~~~~~~~ Poetry & Python dependencies ~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

ARG PIP_VERSION=23.0.1
RUN pip install "pip==${PIP_VERSION}"

RUN pip install "mkdocs-glightbox==0.3.1"

COPY . /docs
