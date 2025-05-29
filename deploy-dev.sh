#!/bin/bash
set -e

# Update system and install essentials
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git unzip wget

# Optional: install ffmpeg, libgl for YOLOv8 image display
sudo apt install -y ffmpeg libgl1

# Set project directory
PROJECT_DIR=~/YoloService

# Create virtual environment if not exists
if [ ! -d "$PROJECT_DIR/venv" ]; then
  python3 -m venv "$PROJECT_DIR/venv"
fi

# Activate venv and install requirements
source "$PROJECT_DIR/venv/bin/activate"
pip install --upgrade pip

pip install -r "$PROJECT_DIR/torch-requirements.txt"
# Install your app requirements
pip install -r "$PROJECT_DIR/requirements.txt"


# Copy the systemd service file for dev
sudo cp ~/yolo-dev.service /etc/systemd/system/

# Reload systemd and restart the dev service
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl restart yolo-dev.service
sudo systemctl enable yolo-dev.service

# Verify the dev service is running
if ! systemctl is-active --quiet yolo-dev.service; then
  echo "❌ yolo-dev.service is not running."
  sudo systemctl status yolo-dev.service --no-pager
  exit 1
fi

echo "✅ yolo-dev.service is running successfully."
