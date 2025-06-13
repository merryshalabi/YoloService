#!/bin/bash

set -e

echo "📦 Updating system and installing dependencies..."
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git unzip wget ffmpeg libgl1

echo "🐳 Removing conflicting Docker packages (containerd)..."
sudo apt-get remove -y docker docker.io docker-engine docker-compose containerd containerd.io || true
sudo apt-get autoremove -y
sudo apt-get update

echo "📦 Installing Docker via official script..."
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh


# Optional: add user to docker group
sudo usermod -aG docker $USER || true


# Set project directory
PROJECT_DIR=~/YoloService


echo "🐍 Setting up Python environment..."
if [ ! -d "$PROJECT_DIR/venv" ]; then
  python3 -m venv "$PROJECT_DIR/.venv"
fi

source "$PROJECT_DIR/venv/bin/activate"
pip install --upgrade pip
pip install -r "$PROJECT_DIR/torch-requirements.txt"
pip install -r "$PROJECT_DIR/requirements.txt"

echo "🐳 Starting YOLO service with Docker Compose..."
cd "$PROJECT_DIR"
docker compose -f docker-compose.prod.yaml down || true
docker compose -f docker-compose.prod.yaml up -d --build

echo "✅ YOLO service is up. Ready for API testing."
