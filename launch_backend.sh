#!/bin/sh
set -eux
cd /home/ubuntu/waterer && /usr/bin/make -f /home/ubuntu/waterer/Makefile up-backend
