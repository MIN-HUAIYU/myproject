# GitHub Actions CI/CD 部署配置指南

## 概述

该项目已配置 GitHub Actions CI/CD 工作流，自动部署代码到服务器 `139.224.207.84`。

**工作流说明：**
- 触发条件：每次推送到 main 分支
- 构建：Node.js 前端构建
- 部署：并行部署前端和后端
- 验证：自动验证部署状态

---

## 1. GitHub 配置步骤

### 步骤 1：获取 SSH 私钥

你的 SSH 私钥位置：`C:\Users\user\.ssh\id_ed25519`

### 步骤 2：在 GitHub 中配置 SSH 私钥

1. 打开你的 GitHub 仓库
2. 进入 **Settings** → **Secrets and variables** → **Actions**
3. 点击 **New repository secret**
4. 填写以下信息：
   - **Name**: `SSH_PRIVATE_KEY`
   - **Value**: 复制 `C:\Users\user\.ssh\id_ed25519` 文件的全部内容

   ```bash
   # 在 PowerShell 中查看私钥内容
   Get-Content C:\Users\user\.ssh\id_ed25519
   ```

5. 点击 **Add secret** 保存

### 步骤 3：验证 Secret 配置

返回 **Secrets and variables** → **Actions**，你应该看到 `SSH_PRIVATE_KEY` 已列出。

---

## 2. 工作流文件说明

### 文件位置
`.github/workflows/deploy.yml`

### 工作流步骤

1. **Checkout 代码**
   - 从 GitHub 拉取最新代码

2. **配置 SSH 密钥**
   - 从 GitHub Secrets 读取 SSH 私钥
   - 配置已知主机

3. **构建前端**
   - Node.js 环境设置（v20）
   - 运行 `npm install` 和 `npm run build`

4. **部署前端**
   - 清理目录：`/www/wwwroot/aiaiai`
   - 上传前端构建文件
   - 设置权限（755）和所有者（www:www）

5. **部署后端**
   - 上传后端代码到 `/root/drawing_information/backend`
   - 安装 Python 依赖
   - 重启 systemd 服务：`drawing-ocr`

6. **验证部署**
   - 检查前端文件
   - 检查后端服务状态
   - 显示部署时间

---

## 3. 服务器配置

### 已配置项

- **服务器地址**：`139.224.207.84`
- **认证方式**：SSH 密钥认证
- **部署用户**：`root`
- **前端部署路径**：`/www/wwwroot/aiaiai`
- **后端部署路径**：`/root/drawing_information/backend`
- **后端服务名**：`drawing-ocr`
- **服务管理器**：systemd

### systemd 服务配置

**文件位置**：`/etc/systemd/system/drawing-ocr.service`

**主要配置**：
```ini
[Unit]
Description=Drawing OCR Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/drawing_information/backend
ExecStart=/usr/bin/python3 -m uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

---

## 4. 使用方法

### 自动部署触发

只需推送代码到 `main` 分支：

```bash
git add .
git commit -m "your commit message"
git push origin main
```

### 监控部署过程

1. 打开 GitHub 仓库
2. 进入 **Actions** 标签
3. 查看最新的工作流运行
4. 点击运行以查看详细日志

### 常见问题

**问题 1：SSH 连接失败**
- 检查 SSH 私钥是否正确复制到 GitHub Secrets
- 确保服务器防火墙允许 SSH 连接

**问题 2：部署后服务无法启动**
- 查看工作流日志中的错误信息
- SSH 连接服务器手动检查：`systemctl status drawing-ocr`

**问题 3：前端页面无法访问**
- 检查 Nginx 配置是否正确指向 `/www/wwwroot/aiaiai`
- 检查文件权限和所有者

---

## 5. 服务器环境信息

| 组件 | 版本 | 状态 |
|------|------|------|
| Python | 3.6.8 | ✓ |
| Node.js | v20.19.2 | ✓ |
| NPM | 10.8.2 | ✓ |
| systemd | - | ✓ |
| Nginx | - | ✓ |

---

## 6. 故障排除命令

在服务器上手动调试时使用：

```bash
# 查看服务状态
systemctl status drawing-ocr

# 查看服务日志
journalctl -u drawing-ocr -n 50

# 手动重启服务
systemctl restart drawing-ocr

# 查看前端部署
ls -la /www/wwwroot/aiaiai

# 检查后端进程
ps aux | grep uvicorn
```

---

## 7. 下一步

部署配置完成后：

1. **推送代码**到 main 分支测试自动部署
2. **监控日志**确认部署成功
3. **访问服务**验证功能正常

---

**创建日期**：2025-12-24
**工作流版本**：1.0
