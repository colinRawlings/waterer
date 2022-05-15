makefile_path := $(abspath $(lastword $(MAKEFILE_LIST)))
makefile_dir := $(patsubst %/,%,$(dir $(makefile_path)))

FRONTEND_DIR = ${makefile_dir}
BACKEND_DIR = ${makefile_dir}/backend
BACKEND_VENV_DIR = ${BACKEND_DIR}/.venv

backend_startup_script := $(makefile_dir)/launch_backend.sh
frontend_startup_script := $(makefile_dir)/launch_frontend.sh

SERVER_IP = 192.168.8.103
SERVER_USER = ubuntu
SERVER_TIMEZONE = Europe/Zurich

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

install-ssh:
	sudo apt update
	sudo apt install -y openssh-server
	sudo systemctl enable ssh
	sudo systemctl start ssh

install-host-tools: install-ssh
ifdef OS
	${COMMENT_CHAR} TODO: node, npm, yarn, angular, arduino
else
	# This probably only works on ubuntu
	sudo apt update
	#
	sudo apt install -y build-essential gcc make clang-format
	#
	sudo apt-get install -y python3-dev\
	 python3-venv\
	 python3-pip
	# matplotlib (inc. deps)
	sudo apt install -y python3-matplotlib
	# node
	curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
	sudo apt install -y nodejs
	sudo npm install -g -y yarn
	sudo npm install -g -y lite-server
	# bluetooth
	sudo apt install -y bluez
endif

install-host-dev-tools: install-host-tools
	# This probably only works on debian
	sudo apt update
	# installing arduino IDE
	sudo snap install arduino
	sudo usermod -aG dialout $(shell whoami)
	sudo npm install -g -y @angular/cli


install-dev: | install-host-dev-tools venv
	${COMMENT_CHAR} Python Tools
	${BACKEND_VENV_PYTHON} -m pip install pip-tools
	${BACKEND_VENV_PIP_SYNC} ${BACKEND_DIR}/requirements/dev.txt
	${COMMENT_CHAR} Formatting
	${BACKEND_VENV_PYTHON} -m pre_commit install --install-hooks
	${COMMENT_CHAR} Install backend
	${BACKEND_VENV_PYTHON} -m pip install -e ${BACKEND_DIR}
	${COMMENT_CHAR} npm install -g pyright@1.1.240
	${COMMENT_CHAR} Install Frontend
	cd ${FRONTEND_DIR} && yarn install --production=false
	cd ${FRONTEND_DIR}/node_modules/@types && ${RENAME_CMD} plotly.js plotly.js-dist ; exit 0

install-fw:
	sudo cp ${makefile_dir}/BLE_fw/rtl8761b_config /lib/firmware/rtl_bt/rtl8761bu_config.bin
	sudo cp ${makefile_dir}/BLE_fw/rtl8761b_fw /lib/firmware/rtl_bt/rtl8761bu_fw.bin


install: | install-host-tools venv
	${COMMENT_CHAR} Install Backend
	${BACKEND_VENV_PYTHON} -m pip install pip-tools
	${BACKEND_VENV_PIP_SYNC} ${BACKEND_DIR}/requirements/base.txt
	${BACKEND_VENV_PYTHON} -m pip install -e ${BACKEND_DIR}
	${COMMENT_CHAR} Install Frontend
	cd ${FRONTEND_DIR} && yarn install --production=true
	${COMMENT_CHAR} For pi run: make install-service; make install-fw


install-services: | backend_startup_script frontend_startup_script
	sudo cp ${makefile_dir}/waterer_backend.service /etc/systemd/system/waterer_backend.service
	systemctl enable waterer_backend
	sudo cp ${makefile_dir}/waterer_frontend.service /etc/systemd/system/waterer_frontend.service
	systemctl enable waterer_frontend


set-timezone:
	sudo timedatectl set-timezone ${SERVER_TIMEZONE}
	timedatectl

#

push-frontend:
	ng build
ifdef OS
	${COMMENT_CHAR} Run: wsl scp -r ./dist	$(SERVER_USER)@$(SERVER_IP):/home/ubuntu/waterer/
else
	scp -r ./dist  $(SERVER_USER)@$(SERVER_IP):/home/ubuntu/waterer/
endif
	# don't forget to make waterer-shell && cd waterer && git pull && make restart-services

#

backend_startup_script: ${backend_startup_script}

${backend_startup_script}:
	echo "#!/bin/sh" > ${backend_startup_script}
	echo "set -eux" >> ${backend_startup_script}
	echo "cd $(makefile_dir) && $(shell which make) -f $(makefile_dir)/Makefile up-backend" >> ${backend_startup_script}
	chmod +x ${backend_startup_script}

frontend_startup_script: ${frontend_startup_script}

${frontend_startup_script}:
	echo "#!/bin/sh" > ${frontend_startup_script}
	echo "set -eux" >> ${frontend_startup_script}
	echo "cd $(makefile_dir) && $(shell which make) -f $(makefile_dir)/Makefile up-frontend" >> ${frontend_startup_script}
	chmod +x ${frontend_startup_script}

#

up-frontend-dev: venv
	${BACKEND_VENV_PYTHON} ${makefile_dir}/make_templates.py
	cd ${FRONTEND_DIR} && yarn start

# useful for the rpi that lacks the power to build the frontend
up-frontend: venv
	${BACKEND_VENV_PYTHON} ${makefile_dir}/make_templates.py
	cd ${FRONTEND_DIR} && lite-server


up-backend-dev: export WATERER_FAKE_DATA=1
up-backend-dev:
	${BACKEND_VENV_PYTHON} -m waterer_backend.BLE.run_server

up-backend:
	${BACKEND_VENV_PYTHON} -m waterer_backend.BLE.run_server

tests-backend:
	${BACKEND_VENV_PYTHON} -m pytest ${makefile_dir}/backend/tests
	${ACTIVATE_CMD} && pyright --verbose

# waterer service
.PHONY: waterer-shell restart-services up-status

up-backend-service:
	systemctl start waterer_backend.service

up-frontend-service:
	systemctl start waterer_frontend.service

make up-services: | up-backend-service up-frontend-service

#

down-backend-service:
	systemctl start waterer_backend.service

down-frontend-service:
	systemctl start waterer_frontend.service

make down-services: | down-backend-service up-frontend-service

#

up-backend-status:
	journalctl -u waterer_backend.service -f

up-frontend-status:
	journalctl -u waterer_frontend.service -f

#

make restart-backend-service:
	systemctl restart waterer_backend.service

make restart-frontend-service:
	systemctl restart waterer_frontend.service

restart-services: | restart-frontend-service restart-backend-service

#

waterer-shell:
	ssh $(SERVER_USER)@$(SERVER_IP)


pip-list:
	${BACKEND_VENV_PYTHON} -m pip list
