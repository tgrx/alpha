# -----------------------------------------------
# OS-depend actions

ifeq ($(OS), Windows_NT)

define log
	@echo ">>>>>>>>>>>>>>>>    $(1)"
endef

else

define log
	@tput bold 2>/dev/null || exit 0
	@tput setab 0  2>/dev/null || exit 0
	@tput setaf 4  2>/dev/null || exit 0
	@echo ">>>>>>>>>>>>>>>>    $(1)    "
	@tput sgr0  2>/dev/null || exit 0
endef

endif


# -----------------------------------------------
# independent variables

DIR_VENV := $(shell $(PIPENV) --venv 2>/dev/null)
DIR_REPO := $(realpath ./)

# -----------------------------------------------
# OS-depend variables

ifeq ($(OS), Windows_NT)

DIR_REPO := $(abspath $(shell cd))

else

DIR_REPO := $(abspath $(shell pwd))

endif


# -----------------------------------------------
# Paths

DIR_SRC := $(abspath $(DIR_REPO)/src)
DIR_TESTS := $(abspath $(DIR_REPO)/tests)

DIR_SCRIPTS = $(abspath $(DIR_SRC)/scripts)


# -----------------------------------------------
# Virtualenv-depend variables

ifeq ($(shell python "$(DIR_SRC)/framework/util/venv.py"), True)

IN_VENV := True
RUN :=
PIPENV_INSTALL := echo Cannot create venv under venv

else

IN_VENV := False
RUN := $(PIPENV) run
PIPENV_INSTALL := $(PIPENV) install

endif


# -----------------------------------------------
# calculated variables

PYTHON := $(RUN) python
