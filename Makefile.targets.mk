.PHONY: run
run:
	$(call log, starting local web server)
	$(LOCAL_RUN)


.PHONY: run-prod
run-prod:
	$(call log, starting local web server)
	$(RUN) gunicorn --config="$(DIR_SCRIPTS)/gunicorn.conf.py" $(WSGI_APPLICATION)


.PHONY: format
format:
	$(call log, reorganizing imports & formatting code)
	$(RUN) isort --virtual-env="$(DIR_VENV)" "$(DIR_SRC)" "$(DIR_TESTS)"
	$(RUN) black "$(DIR_SRC)" "$(DIR_TESTS)"


.PHONY: test
test:
	$(call log, running tests)
	$(RUN) pytest
	$(RUN) isort --virtual-env="$(DIR_VENV)" --check-only "$(DIR_SRC)" "$(DIR_TESTS)"
	$(RUN) black --check "$(DIR_SRC)" "$(DIR_TESTS)"


.PHONY: release
release: db data
	$(call log, performing release steps)


.PHONY: sh
sh:
	$(call log, starting Python shell)
	$(RUN) ipython


.PHONY: venv
venv:
	$(call log, installing packages)
	$(PIPENV_INSTALL)


.PHONY: venv-dev
venv-dev:
	$(call log, installing development packages)
	$(PIPENV_INSTALL) --dev


.PHONY: upgrade-venv
upgrade-venv:
	$(call log, upgrading all packages in virtualenv)
	$(PYTHON) $(DIR_SCRIPTS)/upgrade_packages.py


.PHONY: pycharm
pycharm:
	$(call log, setting PyCharm up)
	$(PYTHON) $(DIR_SCRIPTS)/setup_pycharm.py


.PHONY: heroku
heroku:
	$(call log, configuring the Heroku instance)
	$(PYTHON) $(DIR_SCRIPTS)/configure_heroku.py


.PHONY: db
db: migrate
	$(call log, setting DB up)


.PHONY: wait-for-db
wait-for-db:
	$(call log, waiting for DB up)
	$(DIR_SCRIPTS)/wait_for_postgresql.sh


.PHONY: initdb
initdb: resetdb migrate
	$(call log, initializing the DB)


.PHONY: resetdb
resetdb:  dropdb createdb
	$(call log, resetting DB to initial state)


.PHONY: dropdb
dropdb:
	$(call log, dropping the DB)
	psql \
		--echo-all \
		--username=$(shell $(PYTHON) $(DIR_SCRIPTS)/get_db_user.py) \
		--no-password \
		--host=localhost \
		--dbname=postgres \
		--command="DROP DATABASE IF EXISTS \"$(shell $(PYTHON) $(DIR_SCRIPTS)/get_db_name.py)\";"


.PHONY: createdb
createdb:
	$(call log, creating the DB)
	psql \
		--echo-all \
		--username=$(shell $(PYTHON) $(DIR_SCRIPTS)/get_db_user.py) \
		--no-password \
		--host=localhost \
		--dbname=postgres \
		--command="CREATE DATABASE \"$(shell $(PYTHON) $(DIR_SCRIPTS)/get_db_name.py)\";"


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

