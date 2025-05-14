# The setup.sh script to ensure Python virtual environment is set up
setup_sh = """#!/bin/bash

set -e

VENV_DIR=".venv"

# Create venv if not exists
if [ ! -d "$VENV_DIR" ]; then
  echo ">>> Creating virtual environment"
  python3 -m venv "$VENV_DIR"
fi

echo ">>> Activating virtual environment"
source "$VENV_DIR/bin/activate"

echo ">>> Upgrading pip"
pip install --upgrade pip

# Install dependencies
if [ -f requirements.txt ]; then
  echo ">>> Installing from requirements.txt"
  pip install -r requirements.txt
fi

if [ -f torch-requirements.txt ]; then
  echo ">>> Installing from torch-requirements.txt"
  pip install -r torch-requirements.txt
fi