#!/bin/sh

NARGS=$#

if [ ${NARGS} -lt 2 ] ; then
    echo "Syntax: $0 <ip-address> <file>"
    exit 1
fi
IP_ADDRESS=$1
shift
FILE=$1
shift


WEBREPL_ROOT=/Volumes/case-sensitive/webrepl

for i in ${FILE}; do 
    ${WEBREPL_ROOT}/webrepl_cli.py ${IP_ADDRESS}:/$i $i-download
done
