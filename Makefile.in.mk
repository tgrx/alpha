# -----------------------------------------------
# OS-depend actions

ifeq ($(OS), Windows_NT)

define log
	@echo "-*-    $(1)    -*-"
endef

else

define log
	@tput bold 2>/dev/null || exit 0
	@tput setab 0  2>/dev/null || exit 0
	@tput setaf 4  2>/dev/null || exit 0
	@echo -n '-*-    $(1)    -*-'
	@tput sgr0  2>/dev/null || exit 0
	@echo ""
	@tput sgr0  2>/dev/null || exit 0
endef

endif


# -----------------------------------------------
# independent variables

DIR_REPO := $(realpath ./)
DIR_VENV := $(shell poetry env info --path 2>/dev/null)

# -----------------------------------------------
# OS-depend variables

ifeq ($(OS), Windows_NT)

else

endif


# -----------------------------------------------
# Paths

DIR_CONFIG = $(abspath $(DIR_REPO)/config)
DIR_DOCS = $(abspath $(DIR_REPO)/docs)
DIR_SCRIPTS = $(abspath $(DIR_REPO)/scripts)
DIR_SRC := $(abspath $(DIR_REPO)/src)
DIR_TESTS := $(abspath $(DIR_REPO)/tests)


# -----------------------------------------------
# calculated variables

PYTHON := python
MANAGEMENT := $(PYTHON) -m alpha.management
