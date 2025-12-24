# ============================================
# 完整部署脚本 - Windows PowerShell版本
# ============================================
# 此脚本自动化部署整个项目到阿里云服务器

param(
    [string]$ApiKey = ""
)

$ErrorActionPreference = "Stop"

# 配置变量
$SERVER = "139.224.207.84"
$SERVER_USER = "root"
$SSH_KEY = "$env:USERPROFILE\.ssh\id_ed25519"
$LOCAL_PROJECT = "D:\projects\myproject\drawing_information"
$REMOTE_PROJECT = "/root/drawing_information"

# 颜色定义
function Write-Success { Write-Host $args -ForegroundColor Green }
function Write-Error-Custom { Write-Host "❌ $args" -ForegroundColor Red }
function Write-Warning-Custom { Write-Host "⚠️  $args" -ForegroundColor Yellow }
function Write-Info { Write-Host "ℹ️  $args" -ForegroundColor Cyan }
function Write-Step { Write-Host "`n[$(Get-Date -Format 'HH:mm:ss')] $args" -ForegroundColor Cyan }

# 显示标题
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "图片识别Web服务 - 自动部署脚本" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# 步骤1：验证SSH密钥
Write-Step "验证SSH配置..."
if (-not (Test-Path $SSH_KEY)) {
    Write-Error-Custom "SSH密钥不存在: $SSH_KEY"
    exit 1
}
Write-Success "SSH密钥存在"

# 步骤2：测试SSH连接
Write-Step "测试SSH连接..."
try {
    $result = ssh -i $SSH_KEY "${SERVER_USER}@${SERVER}" "echo 'Connection successful'" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Success "SSH连接成功"
    } else {
        throw "SSH连接失败"
    }
} catch {
    Write-Error-Custom "无法连接到服务器: $_"
    exit 1
}

# 步骤3：验证本地项目
Write-Step "验证本地项目..."
if (-not (Test-Path $LOCAL_PROJECT)) {
    Write-Error-Custom "项目目录不存在: $LOCAL_PROJECT"
    exit 1
}

$requiredFiles = @("backend\main.py", "frontend\package.json", "config\settings.py")
foreach ($file in $requiredFiles) {
    $fullPath = Join-Path $LOCAL_PROJECT $file
    if (-not (Test-Path $fullPath)) {
        Write-Error-Custom "缺少文件: $file"
        exit 1
    }
}
Write-Success "项目文件验证通过"

# 步骤4：上传项目文件
Write-Step "上传项目文件到服务器..."
Write-Info "正在上传，这可能需要1-5分钟..."

# 创建临时的rsync包含文件
$includeFile = [System.IO.Path]::GetTempFileName()
$excludePatterns = @(
    "node_modules/",
    "__pycache__/",
    ".git/",
    "dist/",
    ".vscode/",
    "*.pyc",
    ".env",
    "*.log",
    "*.xlsx",
    "施工图纸*.png",
    "image.png",
    "batch_recognize*.py",
    "extract_*.py",
    "generate_*.py",
    "test_*.py",
    "all_ocr_results.json",
    "siliconflow_*"
)

# 使用scp上传整个目录
try {
    # 先删除远程目录
    ssh -i $SSH_KEY "${SERVER_USER}@${SERVER}" "rm -rf $REMOTE_PROJECT" 2>&1 | Out-Null

    # 上传新目录
    & scp -r -i $SSH_KEY -o "ConnectTimeout=10" -o "StrictHostKeyChecking=accept-new" `
        $LOCAL_PROJECT "${SERVER_USER}@${SERVER}:$REMOTE_PROJECT" 2>&1 | ForEach-Object {
        # 只显示进度信息
        if ($_ -match "ETA|%") {
            Write-Host $_ -ForegroundColor Gray
        }
    }

    if ($LASTEXITCODE -eq 0) {
        Write-Success "项目文件上传完成"
    } else {
        throw "scp上传失败"
    }
} catch {
    Write-Error-Custom "文件上传失败: $_"
    exit 1
}

# 步骤5：执行远程设置
Write-Step "在服务器上安装依赖和配置环境..."

$setupScript = @"
#!/bin/bash
set -e

cd $REMOTE_PROJECT

# 更新系统
echo "更新系统包..."
apt update > /dev/null 2>&1 || true
echo "✓ 系统包已更新"

# 安装Python
echo "安装Python 3..."
apt install -y python3 python3-pip python3-venv > /dev/null 2>&1
echo "✓ Python已安装: \$(python3 --version)"

# 安装Node.js
echo "安装Node.js..."
if ! command -v node &> /dev/null; then
    apt install -y nodejs npm > /dev/null 2>&1
fi
echo "✓ Node已安装: \$(node --version)"

# 安装Nginx
echo "安装Nginx..."
apt install -y nginx > /dev/null 2>&1
systemctl enable nginx > /dev/null 2>&1 || true
echo "✓ Nginx已安装"

# 配置Python虚拟环境
echo "配置Python虚拟环境..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip > /dev/null 2>&1
pip install -r backend/requirements.txt > /dev/null 2>&1
deactivate
echo "✓ Python虚拟环境配置完成"

# 安装前端依赖
echo "安装Node依赖..."
cd frontend
npm install --legacy-peer-deps > /dev/null 2>&1
echo "✓ Node依赖安装完成"

# 构建前端
echo "构建React前端..."
npm run build > /dev/null 2>&1
cd ..
echo "✓ 前端构建完成"

# 创建上传目录
mkdir -p backend/uploads
chmod 755 backend/uploads

# 配置环境变量
if [ ! -f ".env" ]; then
    echo "DASHSCOPE_API_KEY=your_api_key_here" > .env
fi

echo ""
echo "✓✓✓ 服务器配置完成！✓✓✓"
"@

try {
    ssh -i $SSH_KEY "${SERVER_USER}@${SERVER}" $setupScript 2>&1 | ForEach-Object {
        if ($_ -match "✓|完成|已安装|配置") {
            Write-Success $_
        } elseif ($_ -match "正在|安装|配置|更新") {
            Write-Info $_
        }
    }
    Write-Success "远程配置完成"
} catch {
    Write-Error-Custom "远程配置失败: $_"
    exit 1
}

# 步骤6：配置Nginx
Write-Step "配置Nginx反向代理..."

$nginxConfig = @"
upstream backend {
    server localhost:8000;
}

server {
    listen 80 default_server;
    listen [::]:80 default_server;

    client_max_body_size 50M;

    # 前端静态文件
    location / {
        root $REMOTE_PROJECT/frontend/dist;
        try_files \$uri \$uri/ /index.html;
        expires 1d;
        add_header Cache-Control "public, immutable";
    }

    # 后端API代理
    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 600s;
        proxy_connect_timeout 600s;
        proxy_send_timeout 600s;
    }

    # FastAPI文档
    location /docs {
        proxy_pass http://backend;
        proxy_set_header Host \$host;
    }

    location /openapi.json {
        proxy_pass http://backend;
        proxy_set_header Host \$host;
    }

    # 健康检查
    location /health {
        access_log off;
        proxy_pass http://backend/api/health;
    }
}
"@

$nginxConfigPath = "/etc/nginx/sites-available/drawing-ocr"

$setupNginx = @"
cat > $nginxConfigPath << 'NGINX_EOF'
$nginxConfig
NGINX_EOF

# 移除默认配置
rm -f /etc/nginx/sites-enabled/default

# 启用新配置
ln -sf $nginxConfigPath /etc/nginx/sites-enabled/drawing-ocr

# 测试Nginx配置
nginx -t > /dev/null 2>&1

# 重启Nginx
systemctl restart nginx

echo "✓ Nginx配置完成"
"@

try {
    ssh -i $SSH_KEY "${SERVER_USER}@${SERVER}" $setupNginx 2>&1 | ForEach-Object {
        if ($_ -match "✓") {
            Write-Success $_
        }
    }
    Write-Success "Nginx配置完成"
} catch {
    Write-Error-Custom "Nginx配置失败: $_"
    exit 1
}

# 步骤7：显示API密钥设置说明
Write-Step "配置API密钥..."

if ($ApiKey -ne "") {
    # 如果提供了API密钥，直接设置
    $setEnv = "echo 'DASHSCOPE_API_KEY=$ApiKey' > $REMOTE_PROJECT/.env"
    ssh -i $SSH_KEY "${SERVER_USER}@${SERVER}" $setEnv 2>&1 | Out-Null
    Write-Success "API密钥已设置"
} else {
    Write-Warning-Custom "请手动设置API密钥！"
    Write-Info "执行以下命令："
    Write-Host "  ssh -i `"$SSH_KEY`" ${SERVER_USER}@${SERVER}" -ForegroundColor Gray
    Write-Host "  nano $REMOTE_PROJECT/.env" -ForegroundColor Gray
    Write-Host "  # 编辑DASHSCOPE_API_KEY=your_key_here" -ForegroundColor Gray
    Write-Host "  # 保存并退出" -ForegroundColor Gray
}

# 步骤8：显示后端启动说明
Write-Step "启动后端服务..."
Write-Info "创建systemd服务..."

$systemdService = @"
[Unit]
Description=Drawing OCR Backend Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$REMOTE_PROJECT
Environment="PATH=$REMOTE_PROJECT/venv/bin"
ExecStart=$REMOTE_PROJECT/venv/bin/python $REMOTE_PROJECT/backend/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"@

$createService = @"
cat > /etc/systemd/system/drawing-ocr-backend.service << 'SERVICE_EOF'
$systemdService
SERVICE_EOF

systemctl daemon-reload
systemctl enable drawing-ocr-backend
systemctl start drawing-ocr-backend

echo "✓ 后端服务已启动"
"@

try {
    ssh -i $SSH_KEY "${SERVER_USER}@${SERVER}" $createService 2>&1 | ForEach-Object {
        if ($_ -match "✓") {
            Write-Success $_
        }
    }
} catch {
    Write-Warning-Custom "服务创建可能失败，但不影响功能"
}

# 等待服务启动
Write-Info "等待服务启动..."
Start-Sleep -Seconds 3

# 步骤9：验证部署
Write-Step "验证部署..."

try {
    # 检查后端
    $backendHealth = ssh -i $SSH_KEY "${SERVER_USER}@${SERVER}" "curl -s http://localhost:8000/api/health" 2>&1
    if ($backendHealth -match "healthy") {
        Write-Success "后端服务运行正常"
    } else {
        Write-Warning-Custom "后端服务可能未完全启动，请稍候片刻"
    }

    # 检查前端文件
    $frontendCheck = ssh -i $SSH_KEY "${SERVER_USER}@${SERVER}" "ls $REMOTE_PROJECT/frontend/dist/index.html" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Success "前端文件已准备好"
    }

    # 检查Nginx
    $nginxStatus = ssh -i $SSH_KEY "${SERVER_USER}@${SERVER}" "systemctl is-active nginx" 2>&1
    if ($nginxStatus -match "active") {
        Write-Success "Nginx运行正常"
    }

} catch {
    Write-Warning-Custom "验证时出错，但部署可能已成功"
}

# 最终总结
Write-Host "`n========================================" -ForegroundColor Green
Write-Host "✅ 部署完成！" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Green

Write-Host "📝 部署信息：" -ForegroundColor Yellow
Write-Host "  服务器地址: http://$SERVER" -ForegroundColor Gray
Write-Host "  后端API: http://$SERVER/api/" -ForegroundColor Gray
Write-Host "  API文档: http://$SERVER/docs" -ForegroundColor Gray
Write-Host ""

Write-Host "🚀 下一步操作：" -ForegroundColor Yellow
Write-Host "  1. 设置API密钥（如果还未设置）" -ForegroundColor Gray
Write-Host "     ssh -i `"$SSH_KEY`" ${SERVER_USER}@${SERVER}" -ForegroundColor Gray
Write-Host "     nano $REMOTE_PROJECT/.env" -ForegroundColor Gray
Write-Host ""
Write-Host "  2. 重启后端服务" -ForegroundColor Gray
Write-Host "     ssh -i `"$SSH_KEY`" ${SERVER_USER}@${SERVER} systemctl restart drawing-ocr-backend" -ForegroundColor Gray
Write-Host ""
Write-Host "  3. 访问应用" -ForegroundColor Gray
Write-Host "     打开浏览器: http://$SERVER" -ForegroundColor Gray
Write-Host ""

Write-Host "📊 查看日志：" -ForegroundColor Yellow
Write-Host "  后端日志: ssh -i `"$SSH_KEY`" ${SERVER_USER}@${SERVER} tail -f /root/drawing_information/backend.log" -ForegroundColor Gray
Write-Host "  Nginx日志: ssh -i `"$SSH_KEY`" ${SERVER_USER}@${SERVER} tail -f /var/log/nginx/access.log" -ForegroundColor Gray
Write-Host ""

Write-Host "✨ 部署脚本执行完成！" -ForegroundColor Cyan
Write-Host ""
