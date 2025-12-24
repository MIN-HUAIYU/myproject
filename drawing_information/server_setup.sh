#!/bin/bash

# 完整的服务器设置脚本
# 此脚本在远程服务器上执行

set -e

REMOTE_PROJECT="/root/drawing_information"

echo "========================================"
echo "图片识别Web服务 - 服务器配置开始"
echo "========================================"
echo ""

# 第1步：更新系统
echo "[1/8] 更新系统包..."
apt update > /dev/null 2>&1 || true
apt upgrade -y > /dev/null 2>&1 || true
echo "✓ 系统更新完成"
echo ""

# 第2步：安装Python环境
echo "[2/8] 安装Python环境..."
apt install -y python3 python3-pip python3-venv > /dev/null 2>&1
echo "✓ Python版本: $(python3 --version)"
echo ""

# 第3步：安装Node.js
echo "[3/8] 安装Node.js..."
if ! command -v node &> /dev/null; then
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - > /dev/null 2>&1
    apt install -y nodejs > /dev/null 2>&1
fi
echo "✓ Node版本: $(node --version)"
echo "✓ NPM版本: $(npm --version)"
echo ""

# 第4步：安装Nginx
echo "[4/8] 安装Nginx..."
apt install -y nginx > /dev/null 2>&1
echo "✓ Nginx已安装"
echo ""

# 第5步：配置Python虚拟环境
echo "[5/8] 配置Python虚拟环境..."
cd "$REMOTE_PROJECT"
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel > /dev/null 2>&1
pip install -r backend/requirements.txt > /dev/null 2>&1
deactivate
echo "✓ Python虚拟环境配置完成"
echo ""

# 第6步：安装前端依赖和构建
echo "[6/8] 构建前端应用..."
cd "$REMOTE_PROJECT/frontend"
npm install --legacy-peer-deps > /dev/null 2>&1
npm run build > /dev/null 2>&1
cd "$REMOTE_PROJECT"
echo "✓ 前端构建完成"
echo ""

# 第7步：创建uploads目录
echo "[7/8] 创建上传目录..."
mkdir -p "$REMOTE_PROJECT/backend/uploads"
chmod 755 "$REMOTE_PROJECT/backend/uploads"
echo "✓ 上传目录创建完成"
echo ""

# 第8步：配置环境变量
echo "[8/8] 配置环境变量..."
if [ ! -f "$REMOTE_PROJECT/.env" ]; then
    cat > "$REMOTE_PROJECT/.env" << 'EOF'
DASHSCOPE_API_KEY=your_api_key_here
EOF
    echo "⚠️  注意：已创建 .env 文件，但需要手动添加API密钥！"
else
    echo "✓ .env文件已存在"
fi
echo ""

echo "========================================"
echo "✓ 服务器配置完成！"
echo "========================================"
echo ""
echo "重要：请编辑 .env 文件添加你的API密钥"
echo "位置: $REMOTE_PROJECT/.env"
echo ""
echo "命令: nano $REMOTE_PROJECT/.env"
echo ""
