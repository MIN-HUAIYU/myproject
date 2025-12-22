import os
import re
from models.ocr_client import AliyunOCRClient
import json
from datetime import datetime


def recognize_all_png_files():
    """识别所有PNG文件"""
    ocr = AliyunOCRClient()
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
                "timestamp": datetime.now().isoformat()
            }
            print(f"[SUCCESS] {png_file} 识别成功")
        except Exception as e:
            print(f"[ERROR] {png_file} 识别失败: {str(e)}")
            results[png_file] = {
                "error": str(e)
            }

    return results, png_files


def extract_equipment_info(ocr_text, image_name):
    """从OCR文本中提取设备信息"""

    data = {
        "图纸名称": image_name,
        "产品编号": "",
        "用户名称": "",
        "设备名称": "",
        "重量": "",
        "热侧介质": "",
        "冷侧介质": "",
        "设计压力": "",
        "设计温度": "",
        "设备型号": "",
        "板片材质": "",
        "设备位号": "",
        "装置名称": ""
    }

    # 从OCR文本中提取板片材质
    if "316L" in ocr_text:
        data["板片材质"] = "316L"
    if "316" in ocr_text and "L" not in ocr_text:
        data["板片材质"] = "316"

    # 提取设计压力（通常格式为数字+MPa或Mpa）
    pressure_pattern = r'(\d+\.?\d*)\s*(?:MPa|Mpa)'
    pressure_match = re.search(pressure_pattern, ocr_text)
    if pressure_match:
        data["设计压力"] = pressure_match.group(1) + " MPa"

    # 提取设计温度（通常格式为数字+℃或°C）
    temp_pattern = r'(\d+\.?\d*)\s*(?:℃|°C)'
    temp_match = re.search(temp_pattern, ocr_text)
    if temp_match:
        data["设计温度"] = temp_match.group(1) + " ℃"

    return data


def save_results_to_json(results, all_data):
    """保存所有识别结果到JSON"""
    output = {
        "timestamp": datetime.now().isoformat(),
        "total_files": len(results),
        "ocr_results": results,
        "extracted_data": all_data
    }

    with open("all_ocr_results.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print("\n[INFO] 识别结果已保存到 all_ocr_results.json")


def main():
    print("[START] 开始批量识别PNG文件...")
    print("=" * 60)

    # 识别所有PNG文件
    results, png_files = recognize_all_png_files()

    # 提取所有设备信息
    all_equipment_data = []
    for png_file in png_files:
        if png_file in results and "ocr_result" in results[png_file]:
            equipment_info = extract_equipment_info(
                results[png_file]["ocr_result"],
                png_file
            )
            all_equipment_data.append(equipment_info)

    # 保存结果
    save_results_to_json(results, all_equipment_data)

    print("\n" + "=" * 60)
    print("[SUMMARY] 批量识别完成")
    print(f"  已识别文件数: {len(png_files)}")
    print(f"  已提取设备数: {len(all_equipment_data)}")

    return all_equipment_data


if __name__ == "__main__":
    equipment_data = main()
