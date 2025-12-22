#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SiliconFlow OCR 批量识别脚本
"""

import os
import json
from models.siliconflow_ocr_client import SiliconFlowOCRClient
from datetime import datetime


def recognize_all_png_files():
    """识别所有PNG文件"""
    ocr = SiliconFlowOCRClient()
    png_files = [f for f in os.listdir('.') if f.endswith('.png')]

    print(f"[INFO] 找到 {len(png_files)} 个PNG文件")
    print("=" * 60)

    results = {}

    for png_file in png_files:
        print(f"\n[Processing] 正在识别: {png_file}")
        try:
            ocr_text = ocr.recognize_local_image(png_file)
            results[png_file] = {
                "ocr_result": ocr_text,
                "timestamp": datetime.now().isoformat(),
                "status": "success",
                "char_count": len(ocr_text)
            }
            print(f"[SUCCESS] {png_file} 识别成功 ({len(ocr_text)} 字符)")
        except Exception as e:
            print(f"[ERROR] {png_file} 识别失败: {str(e)}")
            results[png_file] = {
                "error": str(e),
                "status": "failed"
            }

    return results, png_files


def save_results_to_json(results, png_files):
    """保存所有识别结果到JSON"""
    output = {
        "timestamp": datetime.now().isoformat(),
        "ocr_provider": "SiliconFlow",
        "model": "deepseek-ai/DeepSeek-OCR",
        "total_files": len(png_files),
        "successful": sum(1 for r in results.values() if r.get("status") == "success"),
        "failed": sum(1 for r in results.values() if r.get("status") == "failed"),
        "ocr_results": results
    }

    with open("siliconflow_all_results.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print("\n[INFO] 识别结果已保存到 siliconflow_all_results.json")
    return output


def main():
    print("[START] 开始使用SiliconFlow批量识别PNG文件...")
    print("=" * 60)

    # 识别所有PNG文件
    results, png_files = recognize_all_png_files()

    # 保存结果
    summary = save_results_to_json(results, png_files)

    print("\n" + "=" * 60)
    print("[SUMMARY] 批量识别完成")
    print(f"  总文件数: {summary['total_files']}")
    print(f"  成功识别: {summary['successful']}")
    print(f"  识别失败: {summary['failed']}")

    if summary['successful'] > 0:
        total_chars = sum(
            r.get("char_count", 0) for r in results.values()
            if r.get("status") == "success"
        )
        print(f"  总识别字符数: {total_chars}")

    return results


if __name__ == "__main__":
    results = main()
