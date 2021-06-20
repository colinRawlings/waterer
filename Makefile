makefile_path := $(abspath $(lastword $(MAKEFILE_LIST)))
makefile_dir := $(patsubst %/,%,$(dir $(makefile_path)))

FRONTEND_DIR = ${makefile_dir}
BACKEND_DIR = ${makefile_dir}/backend
BACKEND_VENV_DIR = ${BACKEND_DIR}/.venv

SERVER_IP = 192.168.0.18
SERVER_USER = ubuntu

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
	${BACKEND_VENV_PYTHON} -m pip install pip-tools
	${BACKEND_VENV_PYTHON} -m piptools compile ${BACKEND_DIR}/requirements/base.in
	${BACKEND_VENV_PYTHON} -m piptools compile ${BACKEND_DIR}/requirements/dev.in

install: venv
	${COMMENT_CHAR} TODO: Install node
	${COMMENT_CHAR} TODO: Install yarn
	${COMMENT_CHAR} Install Backend
	${BACKEND_VENV_PYTHON} -m pip install -r ${BACKEND_DIR}/requirements/base.txt
	${BACKEND_VENV_PYTHON} -m pip install ${BACKEND_DIR}
	${COMMENT_CHAR} Install Frontend
	cd ${FRONTEND_DIR} && yarn install --production=true

install-host-tools:
	${COMMENT_CHAR} TODO: Install Arduino IDE/CLI, downgrade board manager to 1.8.2 to allow arduino extension for STL
ifdef OS
	${COMMENT_CHAR} TODO: node, npm, yarn, angular
else
	# This probably only works on ubuntu
	sudo apt-get install python3-dev
	sudo apt-get install python3-venv
	curl -fsSL https://deb.nodesource.com/setup_12.x | sudo -E bash -
	sudo apt install -y nodejs
	sudo npm install --global yarn
	sudo npm install -g @angular/cli
endif

install-dev: venv
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

up-frontend-dev:
	cd ${FRONTEND_DIR} && yarn start

# useful for the rpi that lacks the power to build this
up-frontend:
	cd ${FRONTEND_DIR} && lite-server --baseDir="${FRONTEND_DIR}/dist/waterer/"

push-frontend:
	ng build
	# Run: wsl scp -r ./dist  $(SERVER_USER)@$(SERVER_IP):/home/ubuntu/waterer/

make up-backend:
	${BACKEND_VENV_PYTHON} -m waterer_backend.run_server

tests-backend:
	${BACKEND_VENV_PYTHON} -m pytest ${makefile_dir}/backend/tests
	${ACTIVATE_CMD} && pyright --verbose

pip-list:
	${BACKEND_VENV_PYTHON} -m pip list
