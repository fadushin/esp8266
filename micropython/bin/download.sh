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


if [ ! $(which webrepl_cli.py) ] ; then
    echo "Adding /Volumes/case-sensitive/webrepl to PATH"
    PATH=/Volumes/case-sensitive/webrepl:$PATH
fi

for i in ${FILE}; do 
    webrepl_cli.py ${IP_ADDRESS}:/$i $i-download
done
