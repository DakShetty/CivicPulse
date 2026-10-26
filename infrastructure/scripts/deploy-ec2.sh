#!/usr/bin/env bash
# ==============================================================================
# CivicPulse EC2 In-Host Setup and Service Deployer
# Run this script on the Ubuntu EC2 application host.
# ==============================================================================
set -euo pipefail

echo "==> [1/6] Installing runtime dependencies..."
sudo apt-get update -y
sudo apt-get install -y python3-pip python3-venv git nginx

APP_DIR="/opt/civicpulse"
sudo mkdir -p "$APP_DIR"
sudo chown -R "$USER":"$USER" "$APP_DIR"

echo "==> [2/6] Setting up Python virtual environment..."
python3 -m venv "$APP_DIR/.venv"
source "$APP_DIR/.venv/bin/activate"
pip install --upgrade pip
pip install -r "$APP_DIR/backend/requirements.txt"

echo "==> [3/6] Seeding initial database tables..."
python -m backend.seeds.seed_data

echo "==> [4/6] Creating systemd service for CivicPulse Flask Backend..."
sudo tee /etc/systemd/system/civicpulse-backend.service > /dev/null <<EOF
[Unit]
Description=CivicPulse Flask Application
After=network.target

[Service]
User=$USER
WorkingDirectory=$APP_DIR
EnvironmentFile=$APP_DIR/.env
ExecStart=$APP_DIR/.venv/bin/gunicorn --workers 3 --bind 127.0.0.1:5000 backend.wsgi:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF

echo "==> [5/6] Creating systemd service for CivicPulse Background Worker..."
sudo tee /etc/systemd/system/civicpulse-worker.service > /dev/null <<EOF
[Unit]
Description=CivicPulse Background Queue Worker
After=network.target

[Service]
User=$USER
WorkingDirectory=$APP_DIR
EnvironmentFile=$APP_DIR/.env
ExecStart=$APP_DIR/.venv/bin/python backend/worker.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

echo "==> [6/6] Reloading and starting systemd services..."
sudo systemctl daemon-reload
sudo systemctl enable --now civicpulse-backend.service
sudo systemctl enable --now civicpulse-worker.service

echo "==> CivicPulse services deployed and active!"
sudo systemctl status civicpulse-backend.service --no-pager
