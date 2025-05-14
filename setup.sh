#!/bin/bash

# Setup Python virtual environment and install requirements

VENV_DIR="$HOME/YoloService/.venv"
REQUIREMENTS_FILE="$HOME/YoloService/requirements.txt"
TORCH_REQUIREMENTS_FILE="$HOME/YoloService/torch-requirements.txt"

# Create virtual environment if not exists
if [ ! -d "$VENV_DIR" ]; then
  echo "📦 Creating virtual environment..."
  python3 -m venv "$VENV_DIR"
else
  echo "✅ Virtual environment found at $VENV_DIR"
fi

# Activate venv
source "$VENV_DIR/bin/activate"
echo "✅ Virtual environment activated"

# Upgrade pip
pip install --upgrade pip

# Install Python packages
if [ -f "$REQUIREMENTS_FILE" ]; then
  echo "📦 Installing from requirements.txt"
  pip install -r "$REQUIREMENTS_FILE"
fi

if [ -f "$TORCH_REQUIREMENTS_FILE" ]; then
  echo "📦 Installing from torch-requirements.txt"
  pip install -r "$TORCH_REQUIREMENTS_FILE"
fi