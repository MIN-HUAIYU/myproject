@echo off
echo 正在启动图片识别Web服务...
echo.

:: 创建必要的目录
if not exist "backend\uploads" mkdir backend\uploads

:: 在新窗口中启动后端
echo 启动FastAPI后端服务 (端口 8000)...
start cmd /k "cd backend && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"

:: 等待后端启动
timeout /t 3 /nobreak

:: 在新窗口中启动前端
echo 启动React前端开发服务器 (端口 5173)...
start cmd /k "cd frontend && npm run dev"

echo.
echo 服务已启动！
echo 后端：http://localhost:8000
echo 前端：http://localhost:5173
echo API文档：http://localhost:8000/docs
echo.
pause
