#!/bin/bash

cd "$(dirname "$0")"

VENV_DIR=".venv"
REQUIREMENTS_FILE="requirements.txt"
TORCH_REQUIREMENTS_FILE="torch-requirements.txt"

# Create venv if missing
if [ ! -d "$VENV_DIR" ]; then
  echo "Creating virtual environment..."
  python3 -m venv "$VENV_DIR"
fi

# Activate venv
source "$VENV_DIR/bin/activate"

# Upgrade pip
pip install --upgrade pip

# Install requirements
if [ -f "$REQUIREMENTS_FILE" ]; then
  pip install -r "$REQUIREMENTS_FILE"
fi

if [ -f "$TORCH_REQUIREMENTS_FILE" ]; then
  pip install -r "$TORCH_REQUIREMENTS_FILE"
fi

# Setup systemd service
sudo cp yolo.service /etc/systemd/system/yolo.service
sudo systemctl daemon-reload
sudo systemctl restart yolo.service
sudo systemctl enable yolo.service

# Check service status
if ! systemctl is-active --quiet yolo.service; then
  echo "YOLO service is not running!"
  sudo systemctl status yolo.service
  exit 1
fi