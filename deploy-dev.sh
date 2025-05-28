#!/bin/bash

set -e  # Exit on any error

echo "📦 Setting up Python virtual environment..."

cd ~/YoloService

# Clean up pip cache and old venv if needed
echo "🧼 Cleaning cache and freeing space..."
rm -rf ~/.cache/pip ~/.cache/*
sudo apt clean
df -h

# Recreate the virtual environment cleanly
echo "🛠️ Recreating .venv..."
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip
if [ -f "torch-requirements.txt" ]; then
  echo "🔥 Installing from torch-requirements.txt..."
  pip install -r torch-requirements.txt --no-cache-dir
else
  echo "⚠️ torch-requirements.txt not found, skipping..."
fi

if [ -f "requirements.txt" ]; then
  echo "📦 Installing from requirements.txt..."
  pip install -r requirements.txt --no-cache-dir
else
  echo "⚠️ requirements.txt not found, skipping..."
fi


# Verify uvicorn exists
if [ ! -f ".venv/bin/uvicorn" ]; then
  echo "❌ uvicorn not found in .venv/bin"
  exit 1
fi

echo "✅ Python environment is ready."

# Copy and register systemd service
echo "🔁 Copying yolo-dev.service to /etc/systemd/system/"
sudo cp ~/yolo-dev.service /etc/systemd/system/

echo "🔄 Reloading systemd and restarting service..."
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable yolo-dev.service
sudo systemctl restart yolo-dev.service

# Final check
if ! systemctl is-active --quiet yolo-dev.service; then
  echo "❌ yolo-dev.service is not running."
  sudo systemctl status yolo-dev.service --no-pager
  exit 1
fi

echo "✅ yolo-dev.service is running successfully."
