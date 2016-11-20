#!/bin/sh

NARGS=$#

if [ ${NARGS} -lt 1 ] ; then
    echo "Syntax: $0 <ip-address> [<file>]*"
    exit 1
fi
IP_ADDRESS=$1
shift

FILES=$(ls *.py)
if [ ${NARGS} -gt 1 ] ; then
    FILES=$@
fi

WEBREPL_ROOT=/Volumes/case-sensitive/webrepl

for i in ${FILES}; do 
    ${WEBREPL_ROOT}/webrepl_cli.py $i ${IP_ADDRESS}:/$i
done
