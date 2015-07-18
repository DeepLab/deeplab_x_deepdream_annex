#! /bin/bash
THIS_DIR=`pwd`

if [ $# -eq 0 ]
then
	echo "{}" > $THIS_DIR/lib/Annex/conf/dlxdd.secrets.json
	WITH_CONFIG=$THIS_DIR/lib/Annex/conf/dlxdd.secrets.json
else
	WITH_CONFIG=$1
fi

cd lib/Annex
./setup.sh $WITH_CONFIG
source ~/.bash_profile
sleep 2

cd $THIS_DIR/lib/Annex/lib/Worker/Tasks
ln -s $THIS_DIR/Tasks/* .
ls -la

cd $THIS_DIR/lib/Annex/lib/Worker/Models
ln -s $THIS_DIR/Models/* .
ls -la

cd $THIS_DIR

brew install ffmpeg

pip install --upgrade -r requirements.txt
python setup.py $1

cd lib/Annex
chmod 0400 conf/*
python unveillance_annex.py -firstuse
