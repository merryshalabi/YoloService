#!/bin/bash

# Define the path to your virtual environment
VENV_DIR="/home/ubuntu/YoloService/.venv"
REQUIREMENTS_FILE="/home/ubuntu/YoloService/requirements.txt"
TORCH_REQUIREMENTS_FILE="/home/ubuntu/YoloService/torch-requirements.txt"

# Check if the virtual environment exists
if [ -d "$VENV_DIR" ]; then
  echo "✅ Virtual environment found at $VENV_DIR"
else
  echo "❌ Virtual environment not found at $VENV_DIR"
  echo "📦 Creating a new virtual environment..."
  python3 -m venv "$VENV_DIR"
  if [ $? -ne 0 ]; then
    echo "❌ Failed to create virtual environment. Exiting."
    exit 1
  fi
  echo "✅ Virtual environment created at $VENV_DIR"
fi

# Activate the virtual environment
source "$VENV_DIR/bin/activate"
echo "✅ Virtual environment activated"

# Upgrade pip to avoid compatibility issues
echo "📦 Upgrading pip..."
python -m pip install --upgrade pip || { echo "❌ Failed to upgrade pip."; exit 1; }

# Install dependencies from requirements.txt with debugging
echo "📦 Installing dependencies from requirements.txt..."
python -m pip install --no-cache-dir -r "$REQUIREMENTS_FILE" || { echo "❌ Failed to install dependencies from requirements.txt."; exit 1; }

echo "✅ Dependencies installed from requirements.txt"
echo "📦 Installed Packages after requirements.txt installation:"
python -m pip list

# Install dependencies from torch-requirements.txt with debugging
echo "📦 Installing dependencies from torch-requirements.txt..."
python -m pip install --no-cache-dir -r "$TORCH_REQUIREMENTS_FILE" || { echo "❌ Failed to install dependencies from torch-requirements.txt."; exit 1; }

echo "✅ Dependencies installed from torch-requirements.txt"
echo "📦 Installed Packages after torch-requirements.txt installation:"
python -m pip list

# Ensure pytest is installed
echo "📦 Verifying pytest installation..."
python -m pip show pytest || { echo "❌ pytest not found. Installing..."; python -m pip install pytest; }

# Copy the service file if it exists
if [ -f "yolo.service" ]; then
  sudo cp yolo.service /etc/systemd/system/
else
  echo "❌ yolo.service file not found. Exiting."
  exit 1
fi

# Reload daemon and restart the service
sudo systemctl daemon-reload
sudo systemctl restart yolo.service
sudo systemctl enable yolo.service

# Check if the service is active
if ! systemctl is-active --quiet yolo.service; then
  echo "❌ yolo.service is not running."
  sudo systemctl status yolo.service --no-pager
  exit 1
else
  echo "✅ yolo.service is running."
fi
