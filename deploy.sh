deploy_sh = """#!/bin/bash

set -e

echo ">>> Copying yolo.service to systemd directory"
sudo cp yolo.service /etc/systemd/system/

echo ">>> Reloading systemd daemon"
sudo systemctl daemon-reload

echo ">>> Restarting yolo.service"
sudo systemctl restart yolo.service
sudo systemctl enable yolo.service

echo ">>> Checking service status..."
if ! systemctl is-active --quiet yolo.service; then
  echo "❌ yolo.service is not running."
  sudo systemctl status yolo.service --no-pager
  exit 1
fi

echo "✅ yolo.service is running successfully"