.PHONY: setup
setup: setup-python
	$(call log, configuring the project)


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
		--workers 1 \
		--ws none \
		$(APPLICATION)


.PHONY: run-prod
run-prod:
	$(call log, starting production web server)
	gunicorn --config="$(DIR_CONFIG)/gunicorn.conf.py" $(APPLICATION)


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
qa: tests coverage code-typing code-format code-linters
	$(call log, QA checks)


.PHONY: tests
tests:
	$(call log, running tests)
	rm -f .coverage
	rm -f coverage.xml
	rm -rf htmlcov
	pytest


.PHONY: coverage
coverage:
	$(call log, calculating coverage)
	coverage html
	coverage xml


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
		$(shell $(MANAGEMENT) db-config --host) \
		$(shell $(MANAGEMENT) db-config --port) \
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
		--host=$(shell $(MANAGEMENT) db-config --host) \
		--if-exists \
		--maintenance-db=postgres\
		--port=$(shell $(MANAGEMENT) db-config --port) \
		--username=$(shell $(MANAGEMENT) db-config --username) \
		$(shell $(MANAGEMENT) db-config --db-name)


.PHONY: createdb
createdb:
	$(call log, creating the DB)
	createdb \
		--echo \
		--host=$(shell $(MANAGEMENT) db-config --host) \
		--maintenance-db=postgres\
		--owner=$(shell $(MANAGEMENT) db-config --username) \
		--port=$(shell $(MANAGEMENT) db-config --port) \
		--username=$(shell $(MANAGEMENT) db-config --username)\
		$(shell $(MANAGEMENT) db-config --db-name)


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
	docker system prune --force
