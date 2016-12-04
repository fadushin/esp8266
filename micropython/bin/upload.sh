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

if [ ! $(which webrepl_cli.py) ] ; then
    echo "Adding /Volumes/case-sensitive/webrepl to PATH"
    PATH=/Volumes/case-sensitive/webrepl:$PATH
fi

for i in ${FILES}; do 
    webrepl_cli.py $i ${IP_ADDRESS}:/$(basename $i)
done
