include ./Makefile.in.mk


.PHONY: format
format:
	$(call log, reorganizing imports & formatting code)
	$(RUN) isort --virtual-env="$(DIR_VENV)" "$(DIR_SRC)" "$(DIR_SCRIPTS)" "$(DIR_TESTS)"
	$(RUN) black "$(DIR_SRC)" "$(DIR_SCRIPTS)" "$(DIR_TESTS)"


.PHONY: test
test:
	$(call log, running tests)
	$(RUN) pytest
	$(RUN) isort --virtual-env="$(DIR_VENV)" --check-only "$(DIR_SRC)" "$(DIR_SCRIPTS)" "$(DIR_TESTS)"
	$(RUN) black --check "$(DIR_SRC)" "$(DIR_SCRIPTS)" "$(DIR_TESTS)"


.PHONY: run
run:
	$(call log, starting local web server)
	$(PYTHON) -m app


.PHONY: run-prod
run-prod:
	$(call log, starting local web server)
	$(RUN) gunicorn --config="$(DIR_SCRIPTS)/gunicorn.conf.py" framework.wsgi:application


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


.PHONY: pycharm
pycharm:
	$(call log, setting pycharm up)
	$(PYTHON) $(DIR_SCRIPTS)/setup_pycharm.py


.PHONY: db
db:
	$(call log, setting db up)


.PHONY: data
data:
	$(call log, preparing data)

