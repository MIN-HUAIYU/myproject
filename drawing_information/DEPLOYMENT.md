# 图片识别Web服务 - 部署指南

## 项目结构

```
drawing_information/
├── backend/                    # FastAPI后端
│   ├── main.py                # 主应用文件
│   ├── requirements.txt        # Python依赖
│   └── uploads/               # 上传文件临时目录
├── frontend/                   # React前端
│   ├── src/
│   │   ├── App.jsx            # 主应用组件
│   │   ├── App.css            # 样式文件
│   │   ├── main.jsx           # 入口文件
│   │   └── index.css          # 全局样式
│   ├── package.json           # Node依赖
│   ├── vite.config.js         # Vite配置
│   └── index.html             # HTML入口
├── models/                     # OCR模型文件
│   └── ocr_client.py          # OCR客户端
├── config/                     # 配置文件
│   └── settings.py            # 配置文件
├── .env                        # 环境变量（需要自己配置）
└── README.md
```

## 本地开发部署

### 1. 后端配置和启动

#### 1.1 安装Python依赖

```bash
cd backend
pip install -r requirements.txt
```

#### 1.2 配置环境变量

在项目根目录创建或编辑 `.env` 文件，添加你的API密钥：

```
DASHSCOPE_API_KEY=your_api_key_here
```

#### 1.3 启动FastAPI服务

```bash
cd backend
python main.py
```

服务将运行在 `http://localhost:8000`

可以访问 `http://localhost:8000/docs` 查看API文档

### 2. 前端配置和启动

#### 2.1 安装Node依赖

```bash
cd frontend
npm install
```

或使用yarn：

```bash
cd frontend
yarn install
```

#### 2.2 启动开发服务器

```bash
cd frontend
npm run dev
```

前端将运行在 `http://localhost:5173`

### 3. 测试服务

1. 打开浏览器访问 `http://localhost:5173`
2. 选择一张PNG/JPG图片
3. 点击"开始识别"
4. 等待结果返回并显示在界面上

## 服务器部署（Linux/Ubuntu）

### 1. 连接到服务器

```bash
ssh root@139.224.207.84
```

### 2. 安装依赖

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Python和pip
sudo apt install python3 python3-pip -y

# 安装Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs -y

# 安装Nginx（用于反向代理和前端服务）
sudo apt install nginx -y
```

### 3. 上传项目

在本地执行（Windows PowerShell）：

```powershell
# 如果是第一次上传，建议先压缩项目
# 然后通过scp上传
scp -i $env:USERPROFILE\.ssh\id_ed25519 -r D:\projects\myproject\drawing_information root@139.224.207.84:/root/

# 或使用Git克隆（如果项目在GitHub）
ssh root@139.224.207.84 "git clone your_repo_url /root/drawing_information"
```

### 4. 后端部署

在服务器上执行：

```bash
cd /root/drawing_information

# 创建Python虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r backend/requirements.txt

# 配置环境变量
echo "DASHSCOPE_API_KEY=your_api_key" >> .env

# 使用supervisor或systemd运行服务
```

#### 使用Systemd启动后端服务

创建 `/etc/systemd/system/drawing-ocr-backend.service`：

```ini
[Unit]
Description=Drawing OCR Backend Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/drawing_information
Environment="PATH=/root/drawing_information/venv/bin"
ExecStart=/root/drawing_information/venv/bin/python backend/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl start drawing-ocr-backend
sudo systemctl enable drawing-ocr-backend

# 查看状态
sudo systemctl status drawing-ocr-backend
```

### 5. 前端部署

在服务器上执行：

```bash
cd /root/drawing_information/frontend

# 安装Node依赖
npm install

# 构建前端
npm run build

# 此时会生成dist目录
```

### 6. Nginx配置

编辑 `/etc/nginx/sites-available/drawing-ocr`：

```nginx
upstream backend {
    server localhost:8000;
}

server {
    listen 80;
    server_name 139.224.207.84;

    # 前端静态文件
    location / {
        root /root/drawing_information/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # 后端API代理
    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # FastAPI文档
    location /docs {
        proxy_pass http://backend;
        proxy_set_header Host $host;
    }

    location /openapi.json {
        proxy_pass http://backend;
        proxy_set_header Host $host;
    }
}
```

启用配置：

```bash
sudo ln -s /etc/nginx/sites-available/drawing-ocr /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 7. 验证部署

访问 `http://139.224.207.84` 应该能看到前端界面

### 8. 监控和维护

```bash
# 查看后端日志
sudo journalctl -u drawing-ocr-backend -f

# 查看Nginx日志
sudo tail -f /var/log/nginx/access.log

# 重启服务
sudo systemctl restart drawing-ocr-backend
sudo systemctl restart nginx
```

## 故障排查

### 后端无法连接
- 检查防火墙：`sudo ufw allow 8000`
- 检查环境变量是否正确设置
- 查看日志：`sudo journalctl -u drawing-ocr-backend -f`

### 前端无法访问API
- 确保Nginx反向代理配置正确
- 检查CORS设置
- 查看浏览器控制台错误信息

### 上传文件失败
- 检查uploads目录权限
- 确保磁盘空间充足
- 查看后端日志

## 性能优化（可选）

- 添加Redis缓存识别结果
- 使用CDN加速前端资源
- 添加请求队列处理并发上传
- 使用更强大的服务器硬件

## 安全建议

- 定期更新系统和依赖
- 配置HTTPS（使用Let's Encrypt）
- 限制API请求速率
- 配置防火墙规则
- 定期备份数据
