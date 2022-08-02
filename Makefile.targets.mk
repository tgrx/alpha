.PHONY: setup
setup: setup-python
	$(call log, configuring the project)
	install -d -m 0755 "$(DIR_GARBAGE)/docker-compose"


.PHONY: setup-python
setup-python:
	$(call log, configuring Python)
	$(DIR_SCRIPTS)/setup_python.sh


.PHONY: run
run:
	$(call log, starting application)
	$(ENTRYPOINT)


.PHONY: run-dev
run-dev:
	$(call log, starting development web server)
	uvicorn \
		--host 0.0.0.0 \
		--lifespan off \
		--log-level debug \
		--port 8000 \
		--reload \
		--reload-dir $(DIR_CONFIG) \
		--reload-dir $(DIR_SRC) \
		--reload-include .env \
		--workers 1 \
		--ws none \
		$(APPLICATION)


.PHONY: run-prod
run-prod:
	$(call log, starting production web server)
	gunicorn --config="$(DIR_CONFIG)/gunicorn.conf.py" $(APPLICATION)


.PHONY: docs-run
docs-run:
	$(call log, starting docs server)
	(cd $(DIR_DOCS) && mkdocs serve)


.PHONY: docs-deploy
docs-deploy:
	$(call log, deploying docs)
	(cd $(DIR_DOCS) && mkdocs gh-deploy --force)


.PHONY: format
format:
	$(call log, reorganizing imports & formatting code)
	isort --virtual-env="$(DIR_VENV)" \
		"$(DIR_SRC)" \
		"$(DIR_TESTS)" \
		"$(DIR_SCRIPTS)" \
		"$(DIR_CONFIG)" \
		|| exit 1
	black \
		"$(DIR_SRC)" \
		"$(DIR_TESTS)" \
		"$(DIR_SCRIPTS)" \
		"$(DIR_CONFIG)" \
		|| exit 1


.PHONY: qa
qa: clean-garbage tests coverage code-typing code-format code-linters
	$(call log, QA checks)


.PHONY: tests
tests:
	$(call log, running all tests)
	pytest


.PHONY: tests-unit
tests-unit:
	$(call log, running unit tests)
	pytest -m unit


.PHONY: coverage
coverage:
	$(call log, calculating coverage)
	coverage html
	coverage xml


.PHONY: clean-garbage-coverage
clean-garbage-coverage:
	$(call log, cleaning Coverage garbage)
	coverage erase
	rm -rf "$(DIR_GARBAGE)/coverage"


.PHONY: clean-garbage-mypy
clean-garbage-mypy:
	$(call log, cleaning Mypy garbage)
	rm -rf "$(DIR_GARBAGE)/mypy"


.PHONY: clean-garbage-pytest
clean-garbage-pytest:
	$(call log, cleaning Mypy garbage)
	rm -rf "$(DIR_GARBAGE)/pytest"


.PHONY: clean-garbage
clean-garbage: clean-garbage-mypy clean-garbage-pytest clean-garbage-coverage
	$(call log, cleaning garbage)


.PHONY: code-typing
code-typing:
	$(call log, checking code typing)
	mypy


.PHONY: code-format
code-format:
	$(call log, checking code format)
	isort --virtual-env="$(DIR_VENV)" --check-only \
		"$(DIR_SRC)" \
		"$(DIR_TESTS)" \
		"$(DIR_SCRIPTS)" \
		"$(DIR_CONFIG)" \
		|| exit 1
	black --check \
		"$(DIR_SRC)" \
		"$(DIR_TESTS)" \
		"$(DIR_SCRIPTS)" \
		"$(DIR_CONFIG)" \
		|| exit 1


.PHONY: code-linters
code-linters:
	$(call log, linting)
	flake8


.PHONY: release
release: db data
	$(call log, performing release steps)


.PHONY: sh
sh:
	$(call log, starting Python shell)
	ipython


.PHONY: venv
venv:
	$(call log, installing packages)
	poetry install --no-root


.PHONY: venv-prod
venv-deploy:
	$(call log, installing packages into system)
	poetry install --no-dev --no-root


.PHONY: venv-update
venv-update:
	$(call log, upgrading all packages in virtualenv)
	poetry update


.PHONY: heroku
heroku:
	$(call log, configuring the Heroku instance)
	$(MANAGEMENT) heroku --configure


.PHONY: db
db: migrate
	$(call log, setting DB up)


.PHONY: wait-for-db
wait-for-db:
	$(call log, waiting for DB up)
	$(DIR_SCRIPTS)/wait_online.sh \
		$(shell $(MANAGEMENT) db host) \
		$(shell $(MANAGEMENT) db port) \
		|| exit 1


.PHONY: initdb
initdb: resetdb migrate
	$(call log, initializing the DB)


.PHONY: resetdb
resetdb:  dropdb createdb
	$(call log, resetting DB to initial state)


.PHONY: dropdb
dropdb:
	$(call log, dropping the DB)
	dropdb \
		--echo \
		--host=$(shell $(MANAGEMENT) db host) \
		--if-exists \
		--maintenance-db=postgres\
		--port=$(shell $(MANAGEMENT) db port) \
		--username=$(shell $(MANAGEMENT) db user) \
		$(shell $(MANAGEMENT) db name)


.PHONY: createdb
createdb:
	$(call log, creating the DB)
	createdb \
		--echo \
		--host=$(shell $(MANAGEMENT) db host) \
		--maintenance-db=postgres\
		--owner=$(shell $(MANAGEMENT) db user) \
		--port=$(shell $(MANAGEMENT) db port) \
		--username=$(shell $(MANAGEMENT) db user)\
		$(shell $(MANAGEMENT) db name)


.PHONY: migrations
migrations:
	$(call log, generating migrations)


.PHONY: migrate
migrate:
	$(call log, applying migrations)


.PHONY: data
data: static
	$(call log, preparing data)


.PHONY: static
static:
	$(call log, collecting static)


.PHONY: docker-build
docker-build:
	docker buildx build \
		--build-arg python_version=$(shell cat ./.python-version) \
		--build-arg version=$(shell cat ./version.txt) \
		--compress \
		--platform linux/amd64 \
		--tag alexandersidorov/alpha:latest \
		.

	docker tag \
		alexandersidorov/alpha:latest \
		alexandersidorov/alpha:$(shell cat ./version.txt)


.PHONY: docker-clean
docker-clean:
	docker-compose stop || true
	docker-compose down || true
	docker-compose rm --force || true
