makefile_path := $(abspath $(lastword $(MAKEFILE_LIST)))
makefile_dir := $(patsubst %/,%,$(dir $(makefile_path)))

FRONTEND_DIR = ${makefile_dir}
BACKEND_DIR = ${makefile_dir}/backend
BACKEND_VENV_DIR = ${BACKEND_DIR}/.venv

startup_script := $(makefile_dir)/launch.sh

SERVER_IP = 192.168.8.119
SERVER_USER = ubuntu

ip_config_filepath = $(makefile_dir)/ip_config.json

ifndef
THIS_IP = $(firstword $(shell hostname -I))
endif

ifdef OS
	COMMENT_CHAR = REM
	BASE_PYTHON = py -3.8
	BACKEND_VENV_PYTHON = ${BACKEND_VENV_DIR}/Scripts/python.exe
	BACKEND_VENV_PIP_SYNC = ${BACKEND_VENV_DIR}/Scripts/pip-sync.exe
	RENAME_CMD = rename
	ACTIVATE_CMD = ${BACKEND_VENV_DIR}/Scripts/activate
else
	COMMENT_CHAR = \#
	BASE_PYTHON = python3
	BACKEND_VENV_PYTHON = ${BACKEND_VENV_DIR}/bin/python
	BACKEND_VENV_PIP_SYNC = ${BACKEND_VENV_DIR}/bin/pip-sync
	RENAME_CMD = mv
	ACTIVATE_CMD = source ${BACKEND_VENV_DIR}/bin/activate
endif

.PHONY: info venv

info:
	@echo makefile_dir: ${makefile_dir}
	@echo venv_python: ${BACKEND_VENV_PYTHON}
	@echo IP: ${THIS_IP}

venv: ${BACKEND_VENV_DIR}

${BACKEND_VENV_DIR}:
	${BASE_PYTHON} -m venv --clear ${BACKEND_VENV_DIR}
	${BACKEND_VENV_PYTHON} -m pip install -U pip setuptools wheel
	${BACKEND_VENV_PYTHON} -m pip install -r ${BACKEND_DIR}/requirements/base.txt

requirements: venv
	${BACKEND_VENV_PYTHON} -m pip install pip-tools
	${BACKEND_VENV_PYTHON} -m piptools compile ${BACKEND_DIR}/requirements/base.in
	${BACKEND_VENV_PYTHON} -m piptools compile ${BACKEND_DIR}/requirements/dev.in
	${COMMENT_CHAR} Call install(-dev) to update ...

install: venv
	${COMMENT_CHAR} TODO: Install node
	${COMMENT_CHAR} TODO: Install yarn
	${COMMENT_CHAR} Install Backend
	${BACKEND_VENV_PIP_SYNC} ${BACKEND_DIR}/requirements/base.txt
	${BACKEND_VENV_PYTHON} -m pip install -e ${BACKEND_DIR}
	${COMMENT_CHAR} Install Frontend
	cd ${FRONTEND_DIR} && yarn install --production=true

install-host-tools:
	${COMMENT_CHAR} TODO: Install Arduino IDE/CLI, downgrade board manager to 1.8.2 to allow arduino extension for STL
ifdef OS
	${COMMENT_CHAR} TODO: node, npm, yarn, angular, arduino
else
	# This probably only works on ubuntu
	sudo apt update
	# installing arduino IDE
	sudo snap install arduino
	sudo usermod -aG dialout test
	#
	sudo apt install -y gcc make clang-format-10
	#
	sudo apt-get install -y python3-dev
	sudo apt-get install -y python3-venv
	# node
	curl -fsSL https://deb.nodesource.com/setup_12.x | sudo -E bash -
	sudo apt install -y nodejs
	sudo npm install -g -y yarn
	sudo npm install -g -y @angular/cli
	sudo npm install -g -y lite-server
endif

install-dev: venv
	${COMMENT_CHAR} Python Tools
	${BACKEND_VENV_PYTHON} -m pip install pip-tools
	${BACKEND_VENV_PIP_SYNC} ${BACKEND_DIR}/requirements/dev.txt
	${COMMENT_CHAR} Formatting
	${COMMENT_CHAR} TODO: Install clang-format
	${BACKEND_VENV_PYTHON} -m pre_commit install --install-hooks
	${COMMENT_CHAR} Install backend
	${BACKEND_VENV_PYTHON} -m pip install -e ${BACKEND_DIR}
	${COMMENT_CHAR} npm install -g pyright@1.1.138
	${COMMENT_CHAR} Install Frontend
	cd ${FRONTEND_DIR} && yarn install --production=false
	cd ${FRONTEND_DIR}/node_modules/@types && ${RENAME_CMD} plotly.js plotly.js-dist ; exit 0

up-frontend-dev: venv
	${BACKEND_VENV_PYTHON} ${makefile_dir}/make_templates.py
	cd ${FRONTEND_DIR} && yarn start

# useful for the rpi that lacks the power to build the frontend
up-frontend:
	${BACKEND_VENV_PYTHON} ${makefile_dir}/make_templates.py
	cd ${FRONTEND_DIR} && lite-server

up-service:
	systemctl start waterer.service

down-service:
	systemctl stop waterer.service

push-frontend:
	ng build
ifdef OS
	${COMMENT_CHAR} Run: wsl scp -r ./dist  $(SERVER_USER)@$(SERVER_IP):/home/ubuntu/waterer/
else
	scp -r ./dist  $(SERVER_USER)@$(SERVER_IP):/home/ubuntu/waterer/
endif
	# don't forget to make waterer-shell && cd waterer && git pull && make restart-service

up-backend-dev: export WATERER_FAKE_DATA=1
up-backend-dev:
	${BACKEND_VENV_PYTHON} -m waterer_backend.BLE.run_server

up-backend:
	${BACKEND_VENV_PYTHON} -m waterer_backend.run_server

tests-backend:
	${BACKEND_VENV_PYTHON} -m pytest ${makefile_dir}/backend/tests
	${ACTIVATE_CMD} && pyright --verbose

pip-list:
	${BACKEND_VENV_PYTHON} -m pip list


startup_script: ${startup_script}

${startup_script}:
	echo "cd $(makefile_dir) && $(shell which make) -f $(makefile_dir)/Makefile up-backend &" > ${startup_script}
	echo "cd $(makefile_dir) && $(shell which make) -f $(makefile_dir)/Makefile up-frontend &" >> ${startup_script}
	chmod u+x ${startup_script}

# waterer service
.PHONY: waterer-shell restart-service up-status

up-status:
	journalctl -u waterer.service -f

restart-service:
	systemctl restart waterer.service

waterer-shell:
	ssh $(SERVER_USER)@$(SERVER_IP)
