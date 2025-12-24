from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import os
import sys
from pathlib import Path
import json
from datetime import datetime
from urllib.parse import quote

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from models.ocr_client import AliyunOCRClient
try:
    from .excel_exporter import export_to_excel
except ImportError:
    from excel_exporter import export_to_excel

app = FastAPI(title="Drawing OCR Service")

# 配置CORS以允许React前端访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 临时文件存储目录
UPLOAD_DIR = Path(__file__).parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# 初始化OCR客户端
ocr_client = AliyunOCRClient()


@app.get("/")
async def read_root():
    """健康检查端点"""
    return {"status": "ok", "message": "Drawing OCR Service is running"}


@app.post("/api/ocr")
async def process_image(file: UploadFile = File(...)):
    """
    处理上传的图片并执行OCR识别

    Args:
        file: 上传的图片文件

    Returns:
        JSON格式的识别结果，包含识别文本和其他元数据
    """
    try:
        # 验证文件类型
        allowed_extensions = {".png", ".jpg", ".jpeg", ".gif", ".webp"}
        file_ext = Path(file.filename).suffix.lower()

        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件格式。仅支持：{', '.join(allowed_extensions)}"
            )

        # 保存上传的文件
        file_path = UPLOAD_DIR / file.filename
        file_content = await file.read()

        with open(file_path, "wb") as f:
            f.write(file_content)

        # 调用OCR客户端进行识别
        print(f"正在识别图片：{file.filename}")
        ocr_result = ocr_client.recognize_local_image(str(file_path))

        # 准备响应数据
        response_data = {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "image_file": file.filename,
            "file_size": len(file_content),
            "ocr_result": ocr_result,
            "text_length": len(ocr_result)
        }

        return response_data

    except Exception as e:
        print(f"错误：{str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"OCR处理失败：{str(e)}"
        )


@app.post("/api/export-excel")
async def export_excel(ocr_text: str = Form(...)):
    """
    将 OCR 提取的文本导出为 Excel 表格

    Args:
        ocr_text: OCR 识别的文本内容（表单参数）

    Returns:
        Excel 文件流
    """
    try:
        if not ocr_text or ocr_text.strip() == "":
            raise HTTPException(
                status_code=400,
                detail="OCR 文本不能为空"
            )

        # 生成 Excel
        excel_file = export_to_excel(ocr_text)

        # 生成文件名（使用英文避免编码问题）
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"equipment_info_{timestamp}.xlsx"

        return StreamingResponse(
            iter([excel_file.getvalue()]),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )

    except Exception as e:
        print(f"导出 Excel 失败：{str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"导出 Excel 失败：{str(e)}"
        )


@app.get("/api/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "service": "Drawing OCR Service",
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
