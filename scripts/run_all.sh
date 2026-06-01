#!/usr/bin/env bash
set -euo pipefail

python src/download_data.py
python src/prepare_data.py
python src/eda.py
python src/sql_analysis.py

