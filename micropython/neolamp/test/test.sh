#!/bin/sh

EXE_DIR=$(dirname $0)
. ${EXE_DIR}/env.sh

python3 ${EXE_DIR}/test.py --host=${ESP_IP_ADDRESS} $@
