makefile_path := $(abspath $(lastword $(MAKEFILE_LIST)))
makefile_dir := $(patsubst %/,%,$(dir $(makefile_path)))

FRONTEND_DIR = ${makefile_dir}
BACKEND_DIR = ${makefile_dir}/backend
BACKEND_VENV_DIR = ${BACKEND_DIR}/.venv
BACKEND_VENV_PYTHON = ${BACKEND_VENV_DIR}/bin/python

.PHONY: info devenv

info:
	echo makefile_dir: ${makefile_dir}

venv: ${BACKEND_VENV_DIR}

${BACKEND_VENV_DIR}:
	python3 -m venv --clear ${BACKEND_VENV_DIR}
	${BACKEND_VENV_PYTHON} -m pip install -U pip setuptools wheel
	${BACKEND_VENV_PYTHON} -m pip install -r ${BACKEND_DIR}/requirements/base.txt

reqs: venv
	${BACKEND_VENV_PYTHON} -m pip-compile ${BACKEND_DIR}/requirements/base.in
	${BACKEND_VENV_PYTHON} -m pip-compile ${BACKEND_DIR}/requirements/dev.in

install: venv
	# TODO: Install node
	# TODO: Install yarn
	# Install Frontend
	cd ${FRONTEND_DIR} && yarn install --production=true
	# Install Backend
	${BACKEND_VENV_PYTHON} -m pip install -r ${BACKEND_DIR}/requirements/base.txt
	${BACKEND_VENV_PYTHON} -m pip install ${BACKEND_DIR}


install-dev:
	# TODO: Install Arduino IDE/CLI
	# Python Tools
	${BACKEND_VENV_PYTHON} -m pip install pip-tools
	${BACKEND_VENV_PYTHON} -m pip install -r ${BACKEND_DIR}/requirements/dev.txt
	# Formatting
	# TODO: Install clang-format
	${BACKEND_VENV_DIR}/bin/pre-commit install
	# Install backend
	${BACKEND_VENV_PYTHON} -m pip install -e ${BACKEND_DIR}
	# Install Frontend
	cd ${FRONTEND_DIR} && yarn install --production=false
	mv ${FRONTEND_DIR}/node_modules/@types/plotly.js ${FRONTEND_DIR}/node_modules/@types/plotly.js-dist

up:
	cd ${FRONTEND_DIR} && yarn start &
	${BACKEND_VENV_PYTHON} -m waterer_backend.server
