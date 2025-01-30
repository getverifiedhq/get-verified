#!/bin/sh

set -euo pipefail

if [ "$(id -u)" -ne 0 ]; then
    exit 1
fi

if [ "$#" -ne 1 ]; then
    exit 1
fi

apt update

apt install -y build-essential libbz2-dev libffi-dev libssl-dev python3-dev

cleanup() {
    rm -f "Python-$1.tgz"
    rm -rf "Python-$1"
}

trap cleanup EXIT

wget -O "Python-$1.tgz" https://www.python.org/ftp/python/$1/Python-$1.tgz

tar -xvzf Python-$1.tgz

cd Python-$1

./configure --enable-optimizations

make -j$(nproc)

make altinstall

cd ..

rm -f Python-$1.tgz

rm -rf Python-$1