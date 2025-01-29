#!/bin/sh -e

if [ "$(id -u)" != 0 ];then
    printf "This script requires super user priviliges.\n"
    exit 1
fi

PYTHON_VERSION=3.10.12
INSTALL_UTIL=apt
if ! command -v $INSTALL_UTIL >/dev/null;then
    if command -v apt-get >/dev/null;then
	INSTALL_UTIL=apt-get
    else
	printf "This script requires either apt or apt-get.\n"
	exit 2
    fi
fi

$INSTALL_UTIL update

$INSTALL_UTIL install -y build-essential libbz2-dev libffi-dev libssl-dev python3-dev

wget https://www.python.org/ftp/python/$PYTHON_VERSION/Python-$PYTHON_VERSION.tgz

tar -xvzf Python-$PYTHON_VERSION.tgz

cd Python-$PYTHON_VERSION || exit

./configure --enable-optimizations

make -j$(nproc)

make altinstall

cd ..

rm -f Python-$PYTHON_VERSION.tgz

rm -rf Python-$PYTHON_VERSION
