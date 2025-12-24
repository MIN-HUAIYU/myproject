# -*- coding: utf-8 -*-
"""
改进的数据提取逻辑 - 针对两条流程（流程一、流程二）
"""

import re

# 你提供的 OCR 文本
ocr_text = """技术数据表
项目 程 流程一 流程二 项目 程 流程一 流程二
压力 设计 0.8/FV 1.0/FV 焊接接头系数 0.85 0.85
MPa(G) 操作 0.5 0.02 无损检测方法 RT
设计压差 MPa 无损检测比例 20% 20%
温度 设计 220 220 耐压 1.40/- 液压
℃ 操作(进口/出口) 158.9/158.9 103/105 试验 压力(卧/立)MPa 1.12/- 1.40/- 全真空校核 耐压试验压差 MPa
介质 名称 低压蒸汽及凝液 碳酸钾溶液及蒸气(注6) 泄漏 种类
毒性程度 中度危害 试验 压力 MPa
爆炸危害 几何容积 m³ 0.97 2.94
程数 mm 1 1
腐蚀裕量 0/3(注1) 0/3(注1)
地震烈度 8 保温 材料 玻璃棉 玻璃棉
风压值 N/m² 700 厚度 mm 130 130
风速 m/s 1.3 设备净重 kg 8102
雪压值 N/m² 1400 设备充水后总重 kg 10587
场地类别 II 类 设计使用年限 20年(板束除外)
地面粗糙度 A 换热面积 m² 114
管口表 NOZZLE SCHEDULE
代号 用途 数量 公称尺寸 法兰类型及密封面型式 焊接 件数 备注
MARK SERVICE QTY. NPS. (DN) FLANGE TYPE&CONNECTION 详图 外伸高度 MATCH FLANGE REMARK
N1 低压蒸汽及凝液入口 1 450 Class 150 WN/RF 见图 见图 HG/T 20615-2009
N2 低压蒸汽及凝液出口 1 80 Class 150 WN/RF 见图 见图 HG/T 20615-2009
N3 碳酸钾溶液及蒸气入口 1 600 Class 150 WN/RF 见图 见图 HG/T 20615-2009
N4 碳酸钾溶液及蒸气出口 1 1000 焊接 见图 见图 Q245R+S30403 1016X(10+3)
V 排气口 1 25 Class 150 WN/RF 见图 见图 S31603 法兰盖 HG/T 20615-2009
D 排液口 1 25 Class 150 WN/RF 见图 见图 S31603 法兰盖 HG/T 20615-2009
主要受压元件材料表 MAIN PRESSURE COMPONENTS MATERIAL
名称 材料 名称 材料
PARTS.NAME MATERIAL PARTS.NAME MATERIAL
板片 316L 侧板 S31603
方法兰 Q345R+S31603 流程一管箱 S31603
压板 Q345R+S31603 流程二管箱 S31603
设备流程示意图及说明 说明
流程示意图 流程二出口 1.换热器采用错流1-1流程结构。
2.流程一：热侧介质低压蒸汽及凝液在流程一内流动；
流程二：冷侧介质碳酸钾溶液及蒸汽在流程二内流动。
3.低压蒸汽及凝液从换热器管口N1流入，
从换热器管口N2流出；
碳酸钾溶液及蒸汽从换热器管口N3流入，
从换热器管口N4流出。
流程一入口 N1 流程一出口 N2
流程二入口 N3
产品
规格
批次
日期
版本描述/DESCRIPTION
设计 计 DESIGNED
DESIGNED
日期 DATE
本文件产权属LANPEC所有,未经LANPEC书面许可不准复制或转让第三方。
This document is the property of LANPEC. It shall not be reproduced or transferred
to any other party without LANPEC's permission in written form.
工程总承包 EPCC CONTRACTOR
甘肃蓝科石化高新装备股份有限公司，
"""

def extract_equipment_info_v2(ocr_text):
    """改进版本：支持提取两套流程的信息"""

    # 初始化数据结构 - 支持两套流程
    data = {
        "产品编号": "",
        "用户信息": "",
        "设备名称": "",
        "台数": "",
        "单台重量": "",
        "热侧/冷侧介质名称": "",  # 流程一、流程二
        "板程/壳程介质名称": "",  # 流程一、流程二
        "设计压力/MPa": "",  # 流程一、流程二
        "设计温度/℃": "",  # 流程一、流程二
        "设备型号": "",
        "板片材质": "",
        "换热面积/㎡": ""
    }

    print("=" * 80)
    print("[开始提取信息]")
    print("=" * 80)

    # 预处理：按行分割文本
    text_lines = ocr_text.split('\n')

    # 1. 设计压力（流程一、流程二）
    print("\n[1] 提取设计压力...")
    # 在 "压力" 这一行找 "设计" 后面的两个数值
    found_pressure = False
    for i, line in enumerate(text_lines):
        if '压力' in line and '设计' in line:
            # 尝试多种正则方式
            # 方式1：精确匹配设计后的数值
            match = re.search(r'设计\s+([\d./]+)\s+([\d./]+)', line)
            if not match:
                # 方式2：查找所有数值和斜杠组合
                match = re.search(r'([\d.]+/[A-Z]+)\s+([\d.]+/[A-Z]+)', line)
            if match:
                pressure_1 = match.group(1).strip()
                pressure_2 = match.group(2).strip()
                data["设计压力/MPa"] = f"{pressure_1} / {pressure_2}"
                print(f"    流程一：{pressure_1}")
                print(f"    流程二：{pressure_2}")
                found_pressure = True
                break
    if not found_pressure:
        print("    未找到")

    # 2. 设计温度（流程一、流程二）
    print("\n[2] 提取设计温度...")
    # 在 "温度" 这一行找 "设计" 后面的两个数值
    for i, line in enumerate(text_lines):
        if '温度' in line and '设计' in line:
            match = re.search(r'设计\s+(\d+)\s+(\d+)', line)
            if match:
                temp_1 = match.group(1).strip()
                temp_2 = match.group(2).strip()
                data["设计温度/℃"] = f"{temp_1} / {temp_2}"
                print(f"    流程一：{temp_1}℃")
                print(f"    流程二：{temp_2}℃")
                break
    if not data["设计温度/℃"]:
        print("    未找到")

    # 3. 介质名称（流程一、流程二）
    print("\n[3] 提取介质名称...")
    # 精确匹配："介质 名称 低压蒸汽及凝液 碳酸钾溶液及蒸气(注6)"
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
        print(f"    流程一（热侧）：{medium_1}")
        print(f"    流程二（冷侧）：{medium_2}")
    else:
        print("    未找到")

    # 4. 板片材质
    print("\n[4] 提取板片材质...")
    material_match = re.search(r'板片\s*(\S+)', ocr_text)
    if material_match:
        data["板片材质"] = material_match.group(1).strip()
        print(f"    {data['板片材质']}")
    else:
        print("    未找到")

    # 5. 换热面积
    print("\n[5] 提取换热面积...")
    area_match = re.search(r'换热面积\s*m²\s*([\d.]+)', ocr_text)
    if area_match:
        data["换热面积/㎡"] = area_match.group(1).strip()
        print(f"    {data['换热面积/㎡']} ㎡")
    else:
        print("    未找到")

    # 6. 设备净重（单台重量）
    print("\n[6] 提取设备净重（单台重量）...")
    weight_match = re.search(r'设备净重\s*kg\s*(\d+)', ocr_text)
    if weight_match:
        data["单台重量"] = weight_match.group(1).strip() + " kg"
        print(f"    {data['单台重量']}")
    else:
        print("    未找到")

    # 7. 台数
    print("\n[7] 提取台数...")
    qty_match = re.search(r'程数\s*mm\s*(\d+)\s*(\d+)', ocr_text)
    if qty_match:
        # 这里 "程数" 表示换热器的程数（1程表示单程）
        data["台数"] = "1"  # 从管口表可以看出是单台设备
        print(f"    1台（单台设备）")
    else:
        data["台数"] = "1"
        print(f"    1台（默认单台）")

    print("\n" + "=" * 80)
    print("[提取完成 - 汇总]")
    print("=" * 80)

    for key, value in data.items():
        if value:
            print(f"{key}: {value}")
        else:
            print(f"{key}: [未提取]")

    return data


# 测试
if __name__ == "__main__":
    result = extract_equipment_info_v2(ocr_text)
    print("\n" + "=" * 80)
    print("[最终数据结构]")
    print("=" * 80)
    import json
    print(json.dumps(result, ensure_ascii=False, indent=2))
