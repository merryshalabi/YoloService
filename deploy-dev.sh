#!/bin/bash

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
