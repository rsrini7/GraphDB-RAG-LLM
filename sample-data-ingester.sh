#!/bin/zsh
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
source "venv/bin/activate"
python src/data_ingestion/cli.py --data-path sample_data/ --file-type json
python src/data_ingestion/cli.py --data-path sample_data/ --file-type csv