# 图片识别Web服务

一个完整的Web应用，用于识别图片中的文字内容。使用React前端、FastAPI后端，以及阿里云DashScope OCR服务。

## 功能特性

- 📸 **图片上传**：支持PNG、JPG、GIF、WebP格式
- 🔤 **文字识别**：使用阿里云DashScope API进行高精度OCR识别
- 🎨 **现代UI**：响应式设计，支持移动端
- 📋 **结果复制**：一键复制识别结果到剪贴板
- ⚡ **快速部署**：包含完整的部署脚本和文档

## 快速开始

### 本地开发（Windows）

1. **前置要求**：
   - Python 3.8+
   - Node.js 16+
   - 阿里云DashScope API密钥

2. **配置环境变量**：
   ```bash
   # 在项目根目录创建 .env 文件
   echo DASHSCOPE_API_KEY=your_api_key >> .env
   ```

3. **一键启动**（Windows）：
   ```bash
   start_dev.bat
   ```

   或分别启动：

   后端：
   ```bash
   cd backend
   pip install -r requirements.txt
   python -m uvicorn main:app --reload --port 8000
   ```

   前端：
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

4. **访问应用**：
   - 前端：http://localhost:5173
   - 后端API文档：http://localhost:8000/docs

### 生产部署

详见 [DEPLOYMENT.md](./DEPLOYMENT.md) 文件，包含完整的服务器部署指南。

快速总结：
```bash
# 1. 安装依赖
cd backend && pip install -r requirements.txt
cd ../frontend && npm install

# 2. 构建前端
npm run build

# 3. 配置Nginx反向代理
# (参考 DEPLOYMENT.md)

# 4. 启动后端服务
python backend/main.py
```

## API文档

### OCR识别端点

**POST** `/api/ocr`

请求：
```
Content-Type: multipart/form-data
file: 图片文件（PNG/JPG/GIF/WebP）
```

响应（200 OK）：
```json
{
  "status": "success",
  "timestamp": "2024-01-01T12:00:00.000000",
  "image_file": "image.png",
  "file_size": 12345,
  "ocr_result": "识别出的文字内容...",
  "text_length": 100
}
```

### 健康检查端点

**GET** `/api/health`

响应（200 OK）：
```json
{
  "status": "healthy",
  "service": "Drawing OCR Service",
  "timestamp": "2024-01-01T12:00:00.000000"
}
```

## 项目结构

```
drawing_information/
├── backend/               # FastAPI后端应用
│   ├── main.py           # 主应用入口
│   └── requirements.txt   # Python依赖列表
├── frontend/             # React前端应用
│   ├── src/
│   │   ├── App.jsx       # 主应用组件
│   │   ├── App.css       # 样式
│   │   ├── main.jsx      # 入口
│   │   └── index.css     # 全局样式
│   ├── package.json      # Node依赖
│   ├── vite.config.js    # Vite配置
│   └── index.html        # HTML入口
├── models/               # OCR客户端
│   └── ocr_client.py
├── config/               # 配置管理
│   └── settings.py
├── .env                  # 环境变量（不提交）
├── .env.example          # 环境变量模板
├── DEPLOYMENT.md         # 部署指南
├── start_dev.bat         # Windows本地启动脚本
└── README.md             # 本文件
```

## 技术栈

**前端**：
- React 18
- Vite
- CSS3

**后端**：
- FastAPI
- Uvicorn
- Python 3.8+

**OCR服务**：
- 阿里云 DashScope API
- Qwen VL OCR 2025模型

**部署**：
- Nginx（反向代理）
- Systemd（服务管理）
- Ubuntu/Debian（推荐OS）

## 常见问题

**Q: 如何获取DashScope API密钥？**
A: 访问 https://dashscope.aliyun.com 注册账号后获取API密钥。

**Q: 支持哪些图片格式？**
A: PNG、JPG、JPEG、GIF、WebP

**Q: 上传文件大小有限制吗？**
A: 目前没有硬性限制，但建议图片大小不超过10MB，实际取决于服务器配置。

**Q: 如何扩展功能？**
A: 可以修改后端main.py中的OCR逻辑，或在前端App.jsx中添加新功能。

## 问题排查

遇到问题？请查看：
- [DEPLOYMENT.md](./DEPLOYMENT.md) 中的"故障排查"部分
- 后端日志：`sudo journalctl -u drawing-ocr-backend -f`
- 浏览器控制台（F12）查看前端错误

## 许可证

MIT License

## 作者

Created for Drawing Recognition and Text Extraction

---

**提示**：在生产环境部署前，请务必：
1. 配置HTTPS
2. 设置适当的API速率限制
3. 配置防火墙规则
4. 定期备份数据
5. 监控系统资源使用
