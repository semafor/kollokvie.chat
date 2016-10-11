export PYTHONPATH=$PYTHONPATH:$PWD/src/
PY=`which python3`

python3 -m unittest discover -s tests -v
