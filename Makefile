makefile_path := $(abspath $(lastword $(MAKEFILE_LIST)))
makefile_dir := $(patsubst %/,%,$(dir $(makefile_path)))

FRONTEND_DIR = ${makefile_dir}
BACKEND_DIR = ${makefile_dir}/backend
BACKEND_VENV_DIR = ${BACKEND_DIR}/.venv


ifdef OS
	COMMENT_CHAR = REM
	BASE_PYTHON = py -3.6
	BACKEND_VENV_PYTHON = ${BACKEND_VENV_DIR}/Scripts/python.exe
	RENAME_CMD = rename
	ACTIVATE_CMD = ${BACKEND_VENV_DIR}/Scripts/activate
else
	COMMENT_CHAR = \#
	BASE_PYTHON = python3
	BACKEND_VENV_PYTHON = ${BACKEND_VENV_DIR}/bin/python
	RENAME_CMD = mv
	ACTIVATE_CMD = source ${BACKEND_VENV_DIR}/bin/activate
endif


.PHONY: info devenv

info:
	echo makefile_dir: ${makefile_dir}
	echo venv_python: ${BACKEND_VENV_PYTHON}

venv: ${BACKEND_VENV_DIR}

${BACKEND_VENV_DIR}:
	${BASE_PYTHON} -m venv --clear ${BACKEND_VENV_DIR}
	${BACKEND_VENV_PYTHON} -m pip install -U pip setuptools wheel
	${BACKEND_VENV_PYTHON} -m pip install -r ${BACKEND_DIR}/requirements/base.txt

requirements: venv
	${BACKEND_VENV_PYTHON} -m piptools compile ${BACKEND_DIR}/requirements/base.in
	${BACKEND_VENV_PYTHON} -m piptools compile ${BACKEND_DIR}/requirements/dev.in

install: venv
	${COMMENT_CHAR} TODO: Install node
	${COMMENT_CHAR} TODO: Install yarn
	${COMMENT_CHAR} Install Frontend
	cd ${FRONTEND_DIR} && yarn install --production=true
	${COMMENT_CHAR} Install Backend
	${BACKEND_VENV_PYTHON} -m pip install -r ${BACKEND_DIR}/requirements/base.txt
	${BACKEND_VENV_PYTHON} -m pip install ${BACKEND_DIR}


install-dev:
	${COMMENT_CHAR} TODO: Install Arduino IDE/CLI, downgrade board manager to 1.8.2 to allow arduino extension for STL
	${COMMENT_CHAR} Python Tools
	${BACKEND_VENV_PYTHON} -m pip install pip-tools
	${BACKEND_VENV_PYTHON} -m pip install -r ${BACKEND_DIR}/requirements/dev.txt
	${COMMENT_CHAR} Formatting
	${COMMENT_CHAR} TODO: Install clang-format
	${BACKEND_VENV_PYTHON} -m pre_commit install --install-hooks
	${COMMENT_CHAR} Install backend
	${BACKEND_VENV_PYTHON} -m pip install -e ${BACKEND_DIR}
	${COMMENT_CHAR} npm install -g pyright@1.1.138
	${COMMENT_CHAR} Install Frontend
	cd ${FRONTEND_DIR} && yarn install --production=false
	cd ${FRONTEND_DIR}/node_modules/@types && ${RENAME_CMD} plotly.js plotly.js-dist

up-frontend:
	cd ${FRONTEND_DIR} && yarn start

make up-backend:
	${BACKEND_VENV_PYTHON} -m waterer_backend.run_server

tests-backend:
	${BACKEND_VENV_PYTHON} -m pytest ${makefile_dir}/backend/tests
	${ACTIVATE_CMD} && pyright --verbose

pip-list:
	${BACKEND_VENV_PYTHON} -m pip list
