from models.ocr_client import AliyunOCRClient
import json
from datetime import datetime


def main():
    ocr = AliyunOCRClient()

    # 识别本地图片
    print("正在识别图片...")
    result = ocr.recognize_local_image("施工图纸.png")

    # 保存识别结果到 JSON 文件
    output_data = {
        "timestamp": datetime.now().isoformat(),
        "image_file": "施工图纸.png",
        "ocr_result": result,
        "text_length": len(result)
    }

    with open("ocr_result.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    # 保存纯文本结果
    with open("ocr_result.txt", "w", encoding="utf-8") as f:
        f.write(result)

    print("[SUCCESS] 识别完成！")
    print(f"识别文本长度：{len(result)} 字符")
    print("\n识别内容预览（前200字符）：")
    print("=" * 60)
    print(result[:200])
    print("=" * 60)
    print(f"\n完整结果已保存到：")
    print("  - ocr_result.txt (纯文本)")
    print("  - ocr_result.json (JSON格式)")


if __name__ == "__main__":
    main()
