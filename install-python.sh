apt update

apt install -y build-essential

apt install -y libbz2-dev libffi-dev libssl-dev python3-dev

wget https://www.python.org/ftp/python/3.10.12/Python-3.10.12.tgz

tar -xvzf Python-3.10.12.tgz

cd Python-3.10.12

./configure --enable-optimizations

make -j$(nproc)

make altinstall

cd ..

rm -f Python-3.10.12.tgz

rm -rf Python-3.10.12