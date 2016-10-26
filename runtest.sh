export PYTHONPATH=$PYTHONPATH:$PWD/src/
PY=`which python`

python -m unittest discover -s tests -v
