#!/bin/zsh
export PYTHONPATH="${PYTHONPATH}:${PWD}/src"
source "venv/bin/activate"
python3 check_vector_index.py