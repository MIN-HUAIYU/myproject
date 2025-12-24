#!/bin/bash

# 部署脚本 - 在本地Windows上执行，通过SSH上传文件到服务器

set -e

SERVER="139.224.207.84"
SSH_USER="root"
SSH_KEY="$HOME/.ssh/id_ed25519"
API_KEY="${1:-}"
LOCAL_PROJECT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REMOTE_PROJECT="/root/drawing_information"

echo "========================================"
echo "Drawing OCR Service - Deployment Script"
echo "========================================"
echo ""

# 检查SSH密钥
if [ ! -f "$SSH_KEY" ]; then
    echo "Error: SSH key not found at $SSH_KEY"
    exit 1
fi

# 第1步：测试SSH连接
echo "[1/6] Testing SSH connection..."
ssh -i "$SSH_KEY" "${SSH_USER}@${SERVER}" "echo 'SSH connection OK'" > /dev/null
echo "✓ SSH connection successful"
echo ""

# 第2步：删除远程目录并上传新文件
echo "[2/6] Uploading project files..."
echo "  This may take a few minutes..."
ssh -i "$SSH_KEY" "${SSH_USER}@${SERVER}" "rm -rf $REMOTE_PROJECT" > /dev/null

scp -r -i "$SSH_KEY" \
    -o "ConnectTimeout=10" \
    -o "StrictHostKeyChecking=accept-new" \
    "$LOCAL_PROJECT" "${SSH_USER}@${SERVER}:$REMOTE_PROJECT" > /dev/null 2>&1

echo "✓ Files uploaded successfully"
echo ""

# 第3步：执行远程设置脚本
echo "[3/6] Installing dependencies on server..."

SETUP_CMD='
cd /root/drawing_information

# Update system
apt update > /dev/null 2>&1 || true
echo "✓ System packages updated"

# Install Python
apt install -y python3 python3-pip python3-venv > /dev/null 2>&1
echo "✓ Python installed"

# Install Node.js
if ! command -v node &> /dev/null; then
    apt install -y nodejs npm > /dev/null 2>&1
fi
echo "✓ Node.js installed"

# Install Nginx
apt install -y nginx > /dev/null 2>&1
systemctl enable nginx > /dev/null 2>&1 || true
echo "✓ Nginx installed"

# Setup Python venv
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip > /dev/null 2>&1
pip install -r backend/requirements.txt > /dev/null 2>&1
deactivate
echo "✓ Python venv configured"

# Install frontend dependencies
cd frontend
npm install --legacy-peer-deps > /dev/null 2>&1
npm run build > /dev/null 2>&1
cd ..
echo "✓ Frontend built"

# Create upload directory
mkdir -p backend/uploads
chmod 755 backend/uploads

# Setup .env
if [ ! -f ".env" ]; then
    echo "DASHSCOPE_API_KEY=placeholder" > .env
fi

echo "✓ Server setup completed"
'

ssh -i "$SSH_KEY" "${SSH_USER}@${SERVER}" "$SETUP_CMD"
echo ""

# 第4步：配置API密钥
echo "[4/6] Configuring API key..."
if [ -n "$API_KEY" ]; then
    ssh -i "$SSH_KEY" "${SSH_USER}@${SERVER}" "echo 'DASHSCOPE_API_KEY=$API_KEY' > $REMOTE_PROJECT/.env"
    echo "✓ API key set"
else
    echo "⚠ API key not provided (use: $0 <api_key>)"
    echo "  Will use placeholder value"
fi
echo ""

# 第5步：配置Nginx
echo "[5/6] Configuring Nginx..."

NGINX_CONF='
upstream backend {
    server localhost:8000;
}

server {
    listen 80 default_server;
    listen [::]:80 default_server;

    client_max_body_size 50M;

    location / {
        root /root/drawing_information/frontend/dist;
        try_files $uri $uri/ /index.html;
        expires 1d;
        add_header Cache-Control "public, immutable";
    }

    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 600s;
        proxy_connect_timeout 600s;
        proxy_send_timeout 600s;
    }

    location /docs {
        proxy_pass http://backend;
        proxy_set_header Host $host;
    }

    location /openapi.json {
        proxy_pass http://backend;
        proxy_set_header Host $host;
    }

    location /health {
        access_log off;
        proxy_pass http://backend/api/health;
    }
}
'

NGINX_CMD='
cat > /etc/nginx/sites-available/drawing-ocr << '"'"'NGINX_CONF'"'"'
'"$NGINX_CONF"'
NGINX_CONF

rm -f /etc/nginx/sites-enabled/default
ln -sf /etc/nginx/sites-available/drawing-ocr /etc/nginx/sites-enabled/drawing-ocr

nginx -t > /dev/null 2>&1
systemctl restart nginx

echo "✓ Nginx configured"
'

ssh -i "$SSH_KEY" "${SSH_USER}@${SERVER}" "$NGINX_CMD"
echo ""

# 第6步：启动后端服务
echo "[6/6] Starting backend service..."

BACKEND_CMD='
cd /root/drawing_information
source venv/bin/activate

# Create systemd service
cat > /etc/systemd/system/drawing-ocr-backend.service << '"'"'SERVICE'"'"'
[Unit]
Description=Drawing OCR Backend Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/drawing_information
Environment="PATH=/root/drawing_information/venv/bin"
ExecStart=/root/drawing_information/venv/bin/python /root/drawing_information/backend/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SERVICE

systemctl daemon-reload
systemctl enable drawing-ocr-backend
systemctl start drawing-ocr-backend

sleep 2
systemctl is-active drawing-ocr-backend > /dev/null && echo "✓ Backend service started"
'

ssh -i "$SSH_KEY" "${SSH_USER}@${SERVER}" "$BACKEND_CMD"
echo ""

# 验证
echo "========================================"
echo "✓ Deployment Complete!"
echo "========================================"
echo ""
echo "Access your application:"
echo "  URL: http://139.224.207.84"
echo "  API Docs: http://139.224.207.84/docs"
echo ""
echo "SSH Connection:"
echo "  ssh -i $SSH_KEY ${SSH_USER}@${SERVER}"
echo ""
echo "View logs:"
echo "  journalctl -u drawing-ocr-backend -f"
echo ""
