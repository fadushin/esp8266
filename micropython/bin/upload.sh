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
	if [ -e "/work/src/github/micropython/webrepl/webrepl_cli.py" ]; then
		PATH=/work/src/github/micropython/webrepl:$PATH
	else
		exit "webrepl_cli.py not found"
		exit 1
	fi
fi

for i in ${FILES}; do 
    webrepl_cli.py $i ${IP_ADDRESS}:/${i}
done
