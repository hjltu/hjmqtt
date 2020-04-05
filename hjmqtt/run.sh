#!/bin/bash

# sudo apt install python3-venv

NAME="app.py"
VENV="venv"
DATE=`date +%d-%b-%y_%H%M`
CURR_DIR=${PWD##*/}

echo "usage:"
echo "    ./run.sh [-env, -i]"
echo "    -env  install environment"
echo "    -i    install pip dependencies"
echo "    -s    save backup in tgz"
echo "    -r    run $NAME or \$2"

# install env
if [[ $1 == "-env" ]]; then
    echo "*** INSTALL ENV ***"
    python3 -m venv $VENV
    exit 0
fi

# install app
if [[ $1 == "-i" ]]; then
    echo "*** INSTALL ***"
    $VENV/bin/pip install flask
    exit 0
fi

# save backup
if [[ $1 == "-s" ]]; then
    echo "*** SAVE ***"
    tar cvzf ../${CURR_DIR}-${DATE}.tgz \
    --exclude="$VENV" \
    --exclude="__pycache__" \
    --exclude="*/__pycache__" \
    --exclude="*/*/__pycache__" \
    --exclude="*.pyc" \
    --exclude="*/*.pyc" \
    --exclude="*.swp" \
    --exclude="stat.db" \
    ../$CURR_DIR
    exit 0
fi

# start
if [ $1 == "-r" ]; then
    echo "*** START ***"
    if [ $2 ]; then
        $VENV/bin/python $2
    else
        $VENV/bin/python $NAME
    fi
fi

if [ $# -eq 0 ]; then
    $VENV/bin/python
fi

# 2
#VENV="envsite/bin/flask"
#export FLASK_APP=mysite
#export FLASK_ENV=development
#$VENV run

echo "*** THE END ***"
