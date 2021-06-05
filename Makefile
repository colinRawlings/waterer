makefile_path := $(abspath $(lastword $(MAKEFILE_LIST)))
makefile_dir := $(patsubst %/,%,$(dir $(makefile_path)))

FRONTEND_DIR = ${makefile_dir}
BACKEND_DIR = ${makefile_dir}/backend
BACKEND_VENV_DIR = ${BACKEND_DIR}/.venv
BACKEND_VENV_PYTHON = ${BACKEND_VENV_DIR}/bin/python

.PHONY: info devenv

info:
	echo makefile_dir: ${makefile_dir}

devenv: ${BACKEND_VENV_DIR}

${BACKEND_VENV_DIR}:
	python3 -m venv --clear ${BACKEND_VENV_DIR}
	${BACKEND_VENV_PYTHON} -m pip install -U pip setuptools wheel
	${BACKEND_VENV_PYTHON} -m pip install -r ${BACKEND_DIR}/requirements-dev.txt
	${BACKEND_VENV_DIR}/bin/pre-commit install

install:
	cd ${FRONTEND_DIR} && yarn install --production=true
	cd ${BACKEND_DIR} && pip install .

install-dev:
	cd ${FRONTEND_DIR} && yarn install --production=false
	cd {BACKEND_DIR} && pip install -e .

up:
	cd ${FRONTEND_DIR} && yarn start &
	cd {BACKEND_DIR}
