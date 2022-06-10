[^^^](../../../)

# CONTRIBUTING

## Prerequisites

These items must be installed on your system.

1. [docker](https://www.docker.com/)

If you want to bypass docker-based development
and use your own machine, make sure 
that the following items are installed and are working
on your machine.

1. [make](https://www.gnu.org/software/make/)
2. [poetry](https://python-poetry.org/)
3. [python](https://www.python.org/) with the right version.
    Consider using [pyenv](https://github.com/pyenv/pyenv)
    and `make` will do all stuff for you — see below.
4. [postgresql](https://www.postgresql.org/)

## Run the project

1. `make setup`
2. `make run`
3. open [localhost](http://localhost:8000) in your browser
