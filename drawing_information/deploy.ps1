# 部署脚本 - 用于Windows上传项目到Linux服务器

# 配置
$SERVER = "root@139.224.207.84"
$SSH_KEY = "$env:USERPROFILE\.ssh\id_ed25519"
$LOCAL_PROJECT = "D:\projects\myproject\drawing_information"
$REMOTE_PROJECT = "/root/drawing_information"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "图片识别Web服务 - 自动部署脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 第1步：检查本地文件
Write-Host "[1/4] 检查本地项目文件..." -ForegroundColor Yellow
if (-not (Test-Path $LOCAL_PROJECT)) {
    Write-Host "错误：项目目录不存在！" -ForegroundColor Red
    exit 1
}

Write-Host "✓ 项目目录存在" -ForegroundColor Green
Write-Host ""

# 第2步：创建远程目录
Write-Host "[2/4] 创建远程项目目录..." -ForegroundColor Yellow
ssh -i $SSH_KEY $SERVER "mkdir -p $REMOTE_PROJECT && echo '✓ 目录创建成功'"
Write-Host ""

# 第3步：上传项目文件
Write-Host "[3/4] 上传项目文件到服务器..." -ForegroundColor Yellow
Write-Host "这可能需要几分钟，请耐心等待..." -ForegroundColor Gray

# 排除的目录
$EXCLUDE = @(
    "node_modules",
    ".git",
    "__pycache__",
    "*.pyc",
    "dist",
    ".vscode",
    ".env",
    "*.log"
)

# 创建exclude参数
$excludeParams = $EXCLUDE | ForEach-Object { "--exclude='$_'" } | Join-String -Separator " "

# 执行rsync（如果有的话）或使用scp
$rsyncAvailable = $null -ne (Get-Command rsync -ErrorAction SilentlyContinue)

if ($rsyncAvailable) {
    Write-Host "使用rsync上传..." -ForegroundColor Gray
    rsync -av $excludeParams -e "ssh -i $SSH_KEY" `
        "$LOCAL_PROJECT/" "$SERVER`:$REMOTE_PROJECT/" | ForEach-Object {
        if ($_ -match "^sending|^sent|speedup") {
            Write-Host $_ -ForegroundColor Gray
        }
    }
} else {
    Write-Host "使用scp上传（这会花费一些时间）..." -ForegroundColor Gray
    # 先删除远程目录重新上传
    ssh -i $SSH_KEY $SERVER "rm -rf $REMOTE_PROJECT"

    # 上传
    & "scp.exe" -r -i $SSH_KEY `
        -o "StrictHostKeyChecking=accept-new" `
        "$LOCAL_PROJECT" "$SERVER`:$REMOTE_PROJECT"
}

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ 文件上传成功" -ForegroundColor Green
} else {
    Write-Host "✗ 文件上传失败！" -ForegroundColor Red
    exit 1
}

Write-Host ""

# 第4步：在服务器上执行部署脚本
Write-Host "[4/4] 在服务器上执行部署配置..." -ForegroundColor Yellow
Write-Host ""

$DEPLOY_SCRIPT = @'
#!/bin/bash
set -e

echo "=================================="
echo "服务器端部署开始..."
echo "=================================="
echo ""

# 进入项目目录
cd /root/drawing_information

# 1. 更新系统包
echo "[1/7] 更新系统包..."
apt update > /dev/null 2>&1 || true
echo "✓ 系统包更新完成"
echo ""

# 2. 安装Python 3和pip
echo "[2/7] 检查Python环境..."
if ! command -v python3 &> /dev/null; then
    echo "  → 安装Python 3..."
    apt install -y python3 python3-pip python3-venv > /dev/null 2>&1
fi
echo "✓ Python版本: $(python3 --version)"
echo ""

# 3. 安装Node.js
echo "[3/7] 检查Node.js环境..."
if ! command -v node &> /dev/null; then
    echo "  → 安装Node.js..."
    apt install -y nodejs npm > /dev/null 2>&1
fi
echo "✓ Node.js版本: $(node --version)"
echo "✓ NPM版本: $(npm --version)"
echo ""

# 4. 安装Nginx
echo "[4/7] 检查Nginx..."
if ! command -v nginx &> /dev/null; then
    echo "  → 安装Nginx..."
    apt install -y nginx > /dev/null 2>&1
fi
echo "✓ Nginx已安装"
echo ""

# 5. 创建Python虚拟环境和安装依赖
echo "[5/7] 配置Python环境和安装依赖..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install --upgrade pip -q
pip install -r backend/requirements.txt -q
echo "✓ Python依赖安装完成"
echo ""

# 6. 安装前端依赖和构建
echo "[6/7] 构建React前端..."
cd frontend
npm install --legacy-peer-deps > /dev/null 2>&1
npm run build > /dev/null 2>&1
cd ..
echo "✓ 前端构建完成"
echo ""

# 7. 配置环境变量
echo "[7/7] 配置环境变量..."
if [ ! -f ".env" ]; then
    echo "  → 创建.env文件..."
    cat > .env << 'EOF'
DASHSCOPE_API_KEY=your_api_key_here
EOF
    echo "⚠ 注意：请编辑 .env 文件并添加你的API密钥！"
else
    echo "  → .env文件已存在"
fi
echo "✓ 环境变量配置完成"
echo ""

echo "=================================="
echo "✓ 服务器部署配置完成！"
echo "=================================="
echo ""
echo "下一步：请编辑 .env 文件并添加DASHSCOPE_API_KEY"
echo "命令: nano /root/drawing_information/.env"
echo ""
'@

# 执行远程部署脚本
ssh -i $SSH_KEY $SERVER $DEPLOY_SCRIPT

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "✓ 部署第一阶段完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "接下来的步骤：" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. 配置API密钥（重要！）" -ForegroundColor Cyan
Write-Host "   ssh -i $SSH_KEY $SERVER" -ForegroundColor Gray
Write-Host "   nano /root/drawing_information/.env" -ForegroundColor Gray
Write-Host "   # 添加你的 DASHSCOPE_API_KEY" -ForegroundColor Gray
Write-Host ""
Write-Host "2. 启动后端服务" -ForegroundColor Cyan
Write-Host "   ssh -i $SSH_KEY $SERVER" -ForegroundColor Gray
Write-Host "   cd /root/drawing_information" -ForegroundColor Gray
Write-Host "   source venv/bin/activate" -ForegroundColor Gray
Write-Host "   python backend/main.py" -ForegroundColor Gray
Write-Host ""
Write-Host "3. 配置Nginx（在另一个SSH窗口执行）" -ForegroundColor Cyan
Write-Host "   运行下面生成的Nginx配置脚本" -ForegroundColor Gray
Write-Host ""

Write-Host "按任意键继续配置Nginx..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
