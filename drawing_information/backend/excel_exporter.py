# -*- coding: utf-8 -*-
"""
Excel 导出模块 - 将 OCR 提取的信息写入 Excel 表格
"""

import re
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from io import BytesIO


def extract_equipment_info(ocr_text):
    """从 OCR 文本中提取设备信息 - 改进版本支持两条流程"""
    data = {
        "产品编号": "",
        "用户信息": "",
        "设备名称": "",
        "台数": "",
        "单台重量": "",
        "热侧/冷侧介质名称": "",
        "板程/壳程介质名称": "",
        "设计压力/MPa": "",
        "设计温度/℃": "",
        "设备型号": "",
        "板片材质": "",
        "换热面积/㎡": ""
    }

    # 预处理：按行分割文本
    text_lines = ocr_text.split('\n')

    # 1. 设计压力（流程一、流程二）
    for i, line in enumerate(text_lines):
        if '压力' in line and '设计' in line:
            # 尝试多种正则方式
            match = re.search(r'设计\s+([\d./]+)\s+([\d./]+)', line)
            if not match:
                match = re.search(r'([\d.]+/[A-Z]+)\s+([\d.]+/[A-Z]+)', line)
            if match:
                pressure_1 = match.group(1).strip()
                pressure_2 = match.group(2).strip()
                data["设计压力/MPa"] = f"{pressure_1} / {pressure_2}"
                break

    # 2. 设计温度（流程一、流程二）
    for i, line in enumerate(text_lines):
        if '温度' in line and '设计' in line:
            match = re.search(r'设计\s+(\d+)\s+(\d+)', line)
            if match:
                temp_1 = match.group(1).strip()
                temp_2 = match.group(2).strip()
                data["设计温度/℃"] = f"{temp_1} / {temp_2}"
                break

    # 3. 介质名称（流程一、流程二）
    medium_match = re.search(
        r'介质[^\n]*?名称\s+(\S+)\s+(.+?)(?:毒性|爆炸|$)',
        ocr_text,
        re.DOTALL
    )
    if medium_match:
        medium_1 = medium_match.group(1).strip()
        medium_2 = medium_match.group(2).strip()
        # 移除括号内的注释
        medium_2 = re.sub(r'\([^)]*\)', '', medium_2).strip()
        data["热侧/冷侧介质名称"] = f"{medium_1} / {medium_2}"

    # 4. 板片材质
    material_patterns = [r'316L', r'316', r'钛', r'铜镍', r'不锈钢']
    for pattern in material_patterns:
        if re.search(pattern, ocr_text):
            data["板片材质"] = pattern
            break

    # 5. 换热面积
    area_match = re.search(r'换热面积\s*m²\s*([\d.]+)', ocr_text)
    if area_match:
        data["换热面积/㎡"] = area_match.group(1).strip()

    # 6. 设备净重（单台重量）
    weight_match = re.search(r'设备净重\s*kg\s*(\d+)', ocr_text)
    if weight_match:
        data["单台重量"] = weight_match.group(1).strip() + " kg"

    # 7. 台数
    # 默认为1台（单台设备）
    data["台数"] = "1"

    # 8. 产品编号 (JOB NO.)
    job_match = re.search(r'(?:JOB NO\.|产品编号)\s*\n\s*([A-Z0-9\-]+)', ocr_text)
    if job_match:
        data["产品编号"] = job_match.group(1).strip()

    # 9. 设备名称 (DRAWING TITLE: 或在描述中)
    title_match = re.search(r'(?:DRAWING TITLE:|图纸名称)\s*[：:]*\s*\n\s*([^\n]+)', ocr_text)
    if title_match:
        data["设备名称"] = title_match.group(1).strip()

    # 10. 用户信息 (CLIENT 或 业主)
    client_match = re.search(r'(?:业主|CLIENT)\s*(?:LCLIENT)?\s*(?:PROJECT NO\.)?\s*([^\n]+)', ocr_text)
    if client_match:
        data["用户信息"] = client_match.group(1).strip()

    # 11. 设备型号 (LTB开头 或其他型号)
    model_match = re.search(r'(LTB[^\s\n]+|PHE[^\s\n]+|[A-Z]+\d+[^\s\n]*)', ocr_text)
    if model_match:
        data["设备型号"] = model_match.group(1).strip()

    return data


def create_horizontal_excel(extracted_data_list):
    """
    创建横排 Excel 表格
    Args:
        extracted_data_list: 提取的设备信息列表，每个元素是一个字典
    Returns:
        BytesIO: Excel 文件的字节流
    """
    wb = Workbook()
    ws = wb.active
    ws.title = "设备数据表"

    # 定义表头
    headers = [
        "产品编号",
        "用户信息",
        "设备名称",
        "台数",
        "单台重量",
        "热侧/冷侧介质名称",
        "板程/壳程介质名称",
        "设计压力/MPa",
        "设计温度/℃",
        "设备型号",
        "板片材质",
        "换热面积/㎡"
    ]

    # 设置列宽
    col_widths = [15, 18, 18, 8, 12, 15, 15, 12, 12, 15, 12, 12]
    for col_idx, width in enumerate(col_widths, 1):
        col_letter = chr(64 + col_idx)  # A=65, B=66...
        ws.column_dimensions[col_letter].width = width

    # 定义样式
    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF", size=11)
    border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    data_alignment = Alignment(horizontal='left', vertical='center', wrap_text=True)

    # 写入表头
    for col_idx, header in enumerate(headers, 1):
        col_letter = chr(64 + col_idx)
        cell = ws[f'{col_letter}1']
        cell.value = header
        cell.fill = header_fill
        cell.font = header_font
        cell.border = border
        cell.alignment = Alignment(horizontal='center', vertical='center')

    # 写入数据
    for row_idx, data in enumerate(extracted_data_list, 2):
        for col_idx, header in enumerate(headers, 1):
            col_letter = chr(64 + col_idx)
            cell = ws[f'{col_letter}{row_idx}']
            cell.value = data.get(header, "")
            cell.border = border
            cell.alignment = data_alignment

    # 保存到字节流
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    return output


def export_to_excel(ocr_result_text):
    """
    从 OCR 结果导出 Excel
    Args:
        ocr_result_text: OCR 识别的文本
    Returns:
        BytesIO: Excel 文件的字节流
    """
    # 提取设备信息
    equipment_data = extract_equipment_info(ocr_result_text)

    # 创建 Excel（支持单个或多个设备）
    data_list = [equipment_data]

    # 生成 Excel
    excel_file = create_horizontal_excel(data_list)

    return excel_file
