#!/usr/bin/env bash
set -e

echo "=== [1/7] Updating apt & installing packages ==="
export DEBIAN_FRONTEND=noninteractive
apt-get update -y
apt-get install -y python3-pip python3-venv git nginx curl

# Install Node.js 20 LTS if not present
if ! command -v node &> /dev/null; then
    echo "Installing Node.js..."
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
    apt-get install -y nodejs
fi

echo "=== [2/7] Cloning or pulling latest CivicPulse code ==="
mkdir -p /opt/civicpulse
if [ ! -d "/opt/civicpulse/.git" ]; then
    git clone https://github.com/DakShetty/CivicPulse.git /opt/civicpulse
else
    cd /opt/civicpulse
    git fetch origin
    git reset --hard origin/main
fi

cd /opt/civicpulse

echo "=== [3/7] Setting up Python virtual environment ==="
python3 -m venv /opt/civicpulse/.venv
/opt/civicpulse/.venv/bin/pip install --upgrade pip
/opt/civicpulse/.venv/bin/pip install -r backend/requirements.txt
/opt/civicpulse/.venv/bin/pip install gunicorn

echo "=== [4/7] Generating production .env for EC2 host ==="
cat << 'EOF' > /opt/civicpulse/.env
FLASK_ENV=production
FLASK_DEBUG=0
SECRET_KEY=civicpulse-production-secure-key-2026
PORT=5000
HOST=127.0.0.1
CORS_ORIGIN=*

DATABASE_URL=mysql+pymysql://civicadmin:CPxHDShoyRCK46wO3r!@civicpulse-demo-mysql.cliw0qmyeewp.ap-south-1.rds.amazonaws.com:3306/civicpulse
STORAGE_DRIVER=s3
S3_BUCKET_NAME=civicpulse-demo-storage-572059939036
AWS_REGION=ap-south-1

QUEUE_DRIVER=sqs
SQS_QUEUE_URL=https://sqs.ap-south-1.amazonaws.com/572059939036/civicpulse-demo-jobs-queue
SQS_DLQ_URL=https://sqs.ap-south-1.amazonaws.com/572059939036/civicpulse-demo-jobs-dlq

NOTIFICATION_DRIVER=sns
SNS_TOPIC_ARN=arn:aws:sns:ap-south-1:572059939036:civicpulse-demo-alerts-topic

LOGGING_DRIVER=cloudwatch
CLOUDWATCH_LOG_GROUP=/civicpulse/civicpulse-demo
EOF

echo "=== [5/7] Building frontend production bundle ==="
cd /opt/civicpulse/frontend
npm install
npm run build

echo "=== [6/7] Initializing & seeding RDS MySQL database ==="
cd /opt/civicpulse
/opt/civicpulse/.venv/bin/python -m backend.seeds.seed_data

echo "=== [7/7] Configuring systemd services and Nginx ==="
cat << 'EOF' > /etc/systemd/system/civicpulse-backend.service
[Unit]
Description=CivicPulse Flask API
After=network.target

[Service]
User=root
WorkingDirectory=/opt/civicpulse
EnvironmentFile=/opt/civicpulse/.env
ExecStart=/opt/civicpulse/.venv/bin/gunicorn --workers 3 --bind 127.0.0.1:5000 backend.wsgi:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF

cat << 'EOF' > /etc/systemd/system/civicpulse-worker.service
[Unit]
Description=CivicPulse SQS Background Worker
After=network.target

[Service]
User=root
WorkingDirectory=/opt/civicpulse
EnvironmentFile=/opt/civicpulse/.env
ExecStart=/opt/civicpulse/.venv/bin/python backend/worker.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

cat << 'EOF' > /etc/nginx/sites-available/default
server {
    listen 80 default_server;
    listen [::]:80 default_server;

    root /opt/civicpulse/frontend/dist;
    index index.html;

    server_name _;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:5000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

systemctl daemon-reload
systemctl enable --now civicpulse-backend.service
systemctl enable --now civicpulse-worker.service
systemctl restart civicpulse-backend.service
systemctl restart civicpulse-worker.service
nginx -t
systemctl restart nginx

echo "=== CivicPulse EC2 Deployment Finished Successfully! ==="

