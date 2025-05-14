#!/bin/bash

# Copy the systemd service file
sudo cp ~/yolo.service /etc/systemd/system/

# Reload systemd and restart the service
sudo systemctl daemon-reload
sudo systemctl restart yolo.service
sudo systemctl enable yolo.service

# Verify the service is running
if ! systemctl is-active --quiet yolo.service; then
  echo "❌ yolo.service is not running."
  sudo systemctl status yolo.service --no-pager
  exit 1
fi

echo "✅ yolo.service is running successfully."
