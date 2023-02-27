# Contributing

## Prerequisites

These items must be installed on your system.

1. [docker](https://www.docker.com/)

If you want to bypass docker-based development
and use your own machine, make sure 
that the following items are installed and are working
on your machine.

1. [task](https://taskfile.dev/)
2. [poetry](https://python-poetry.org/)
3. [python](https://www.python.org/) with the right version.
    Consider using [pyenv](https://github.com/pyenv/pyenv)
    and `task` will do all stuff for you — see below.
4. [postgresql](https://www.postgresql.org/)

## Run the project

1. `task docker-up`
2. open [http://localhost:8000](http://localhost:8000) for Webapp
3. open [http://localhost:8801](http://localhost:8801) for PgAdmin
4. open [http://localhost:8802](http://localhost:8802) for Docs
