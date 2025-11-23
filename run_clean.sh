#!/bin/bash
# Helper script to run clean.py with venv activated
cd "$(dirname "$0")"
source venv/bin/activate
python3 clean.py "$@"
