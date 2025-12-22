#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SiliconFlow OCR 客户端测试脚本
"""

from models.siliconflow_ocr_client import SiliconFlowOCRClient
import os


def test_siliconflow_client():
    """测试SiliconFlow OCR客户端"""

    print("[START] 测试SiliconFlow DeepSeek-OCR客户端...")
    print("=" * 60)

    try:
        # 初始化客户端
        print("[INIT] 初始化SiliconFlow客户端...")
        ocr = SiliconFlowOCRClient()
        print("[OK] 客户端初始化成功")

        # 查找第一个PNG文件
        png_files = [f for f in os.listdir('.') if f.endswith('.png')]
        if not png_files:
            print("[ERROR] 未找到PNG文件")
            return False

        test_image = png_files[0]
        print(f"\n[TEST] 开始识别图片: {test_image}")
        print("=" * 60)

        # 执行OCR识别
        result = ocr.recognize_local_image(test_image)

        print("\n[SUCCESS] OCR识别成功!")
        print("=" * 60)
        print(f"\n识别文本长度: {len(result)} 字符")
        print(f"\n[INFO] 识别内容预览已保存")

        # 保存识别结果
        with open("siliconflow_ocr_result.txt", "w", encoding="utf-8") as f:
            f.write(result)

        print("[INFO] 完整识别结果已保存到: siliconflow_ocr_result.txt")

        return True

    except Exception as e:
        print(f"\n[ERROR] 测试失败: {str(e)}")
        print(f"错误类型: {type(e).__name__}")
        return False


if __name__ == "__main__":
    success = test_siliconflow_client()
    exit(0 if success else 1)
