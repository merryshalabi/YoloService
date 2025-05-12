
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
  echo "✅ Virtual environment created at $VENV_DIR"
fi

# Activate the virtual environment
source "$VENV_DIR/bin/activate"
echo "✅ Virtual environment activated"

# Upgrade pip to avoid compatibility issues
pip install --upgrade pip

# Install dependencies from both requirements files, always reinstalling
echo "📦 Installing dependencies from requirements.txt..."
pip install --upgrade --force-reinstall -r "$REQUIREMENTS_FILE"
echo "✅ Dependencies installed from requirements.txt"

echo "📦 Installing dependencies from torch-requirements.txt..."
pip install --upgrade --force-reinstall -r "$TORCH_REQUIREMENTS_FILE"
echo "✅ Dependencies installed from torch-requirements.txt"

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