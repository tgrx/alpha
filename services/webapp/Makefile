PYTHON_VERSION := $(shell cat .python-version)


.PHONY: bootstrap.macos
bootstrap.macos:
	brew install pyenv poetry
	pyenv install --skip-existing --verbose "${PYTHON_VERSION}"
	poetry env use 3.10.9
	poetry install --with dev
