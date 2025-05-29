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

echo "📈 Setting up OpenTelemetry Collector..."

# 1. Install otelcol only if not present
if ! command -v otelcol &> /dev/null; then
  echo "📦 Installing otelcol..."
  curl -LO https://github.com/open-telemetry/opentelemetry-collector-releases/releases/download/v0.97.0/otelcol_0.97.0_linux_amd64.deb
  sudo dpkg -i otelcol_0.97.0_linux_amd64.deb
else
  echo "✅ otelcol already installed."
fi

# 2. Copy config only if changed
echo "⚙️ Checking if config needs update..."
if ! cmp -s "$PROJECT_DIR/otelcol-config.yaml" /etc/otelcol/config.yaml; then
  echo "🔁 Updating config file..."
  sudo cp "$PROJECT_DIR/otelcol-config.yaml" /etc/otelcol/config.yaml
  sudo systemctl restart otelcol
  sleep 5
else
  echo "✅ Config already up to date."
fi

# 3. Ensure service is enabled
sudo systemctl enable otelcol

# 4. Soft health check (doesn't fail the whole pipeline)
echo "🔍 Checking if metrics are exposed..."
if curl -s http://localhost:8889/metrics | grep -q 'system_cpu_time'; then
  echo "✅ OpenTelemetry metrics are exposed."
else
  echo "⚠️ Warning: metrics not available now, but otelcol is running."
  sudo systemctl status otelcol --no-pager
fi


