#!/bin/bash

set -e  # Exit immediately on any error

echo "📦 Setting up Python virtual environment..."

cd ~/YoloService

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
  echo "🛠️ Creating .venv..."
  python3 -m venv .venv
fi

# Activate the virtual environment
source .venv/bin/activate

# Install dependencies
if [ -f "requirements.txt" ]; then
  echo "📦 Installing from requirements.txt..."
  pip install --upgrade pip
  pip install -r requirements.txt
else
  echo "📦 Installing manually (no requirements.txt found)..."
  pip install --upgrade pip
  pip install fastapi uvicorn[standard] ultralytics pillow
fi

# Verify uvicorn exists
if [ ! -f ".venv/bin/uvicorn" ]; then
  echo "❌ uvicorn not found in .venv"
  exit 1
fi

echo "✅ Python environment is ready."

# Copy the systemd service file for dev
echo "🔁 Copying yolo-dev.service to /etc/systemd/system/"
sudo cp ~/yolo-dev.service /etc/systemd/system/

# Reload and restart the service
echo "🚀 Restarting yolo-dev.service..."
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl restart yolo-dev.service
sudo systemctl enable yolo-dev.service

# Verify service is running
if ! systemctl is-active --quiet yolo-dev.service; then
  echo "❌ yolo-dev.service is not running."
  sudo systemctl status yolo-dev.service --no-pager
  exit 1
fi

echo "✅ yolo-dev.service is running successfully."
