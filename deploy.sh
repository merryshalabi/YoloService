#!/bin/bash

set -e

SERVICE_FILE="yolo.service"
VENV_DIR=".venv"

# Copy service file
echo "🔧 Copying systemd service..."
sudo cp $SERVICE_FILE /etc/systemd/system/

# Reload and restart service
echo "🔁 Restarting yolo.service..."
sudo systemctl daemon-reload
sudo systemctl restart yolo.service
sudo systemctl enable yolo.service

# Confirm it's active
if systemctl is-active --quiet yolo.service; then
  echo "✅ yolo.service is running."
else
  echo "❌ yolo.service failed to start."
  sudo systemctl status yolo.service
  exit 1
fi