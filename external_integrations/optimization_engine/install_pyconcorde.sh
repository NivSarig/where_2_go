#!/bin/bash -e

# Name of TSP directory
TSPSOLVER=tspsolver

# Name of concorde env
CONCORDEENV=concorde_env

echo 'Create tspsolver directory'

mkdir -p $TSPSOLVER

cd $TSPSOLVER

echo 'Clone pyconcorde git repository'

git clone https://github.com/jvkersch/pyconcorde

echo 'Create virtual env concorde_env for running in separation'

virtualenv --system-site-packages -p /usr/bin/python3.8 $CONCORDEENV

echo 'Install pyconcorde'

cd pyconcorde
../$CONCORDEENV/bin/python -m pip install -e .
cd ..


cd ..
