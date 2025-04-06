#!/bin/zsh
export PYTHONPATH="${PYTHONPATH}:${PWD}/src"
source "venv/bin/activate"
streamlit run src/app.py