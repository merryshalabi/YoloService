
#!/bin/bash

# Define the path to your virtual environment
VENV_DIR="/home/ubuntu/yolo-app/venv"

# Check if the virtual environment exists
if [ -d "$VENV_DIR" ]; then
  echo "✅ Virtual environment found at $VENV_DIR"
  source "$VENV_DIR/bin/activate"
  echo "✅ Virtual environment activated"
else
  echo "❌ Virtual environment not found at $VENV_DIR"
  exit 1
fi
# copy the .servcie file
sudo cp yolo.service /etc/systemd/system/

# reload daemon and restart the service
sudo systemctl daemon-reload
sudo systemctl restart yolo.service
sudo systemctl enable yolo.service

# Check if the service is active
if ! systemctl is-active --quiet yolo.service; then
  echo "❌ yolo.service is not running."
  sudo systemctl status yolo.service --no-pager
  exit 1
fi