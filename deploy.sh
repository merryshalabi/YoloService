#!/bin/bash

# Deploy and start yolo.service systemd service

echo "🛠 Copying yolo.service to systemd"
sudo cp yolo.service /etc/systemd/system/

echo "🔄 Reloading and restarting service"
sudo systemctl daemon-reload
sudo systemctl restart yolo.service
sudo systemctl enable yolo.service

# Confirm the service is running
if systemctl is-active --quiet yolo.service; then
  echo "✅ yolo.service is active"
else
  echo "❌ yolo.service failed to start"
  sudo systemctl status yolo.service --no-pager
  exit 1
fi