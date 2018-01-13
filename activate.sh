#! /usr/bin/head -n 2
# run with `source activate.sh`
ENV_DIR=env
if [ ! -d $ENV_DIR ]; then
	virtualenv --python=python3 $ENV_DIR
fi
source $ENV_DIR/bin/activate
pip3 install -r requirements.txt

