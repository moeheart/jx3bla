# Created by moeheart at 10/27/2021
# 装备简略信息的生成器，用于从解包表生成装备的种类。

import os
import csv

if __name__ == "__main__":
    # 数据准备
    resultDict = {}

    with open('equip/resources/Custom_Armor.tab')as f:

        data_7 = []
        f_csv = csv.reader(f, delimiter='\t')
        headers = next(f_csv)
        print(headers)

        for row in f_csv:
            line = {}
            for i in range(len(row)):
                line[headers[i]] = row[i]
            data_7.append(line)

        for line in data_7:
            if int(line["Level"]) < 4000:
                continue
            name = line["Name"]
            id = "7,%s" % line["ID"]
            attr = ""
            if "星演" in name:
                attr = "星演"
            if "惊尘" in name:
                attr = "惊尘"
            if "百相" in name:
                attr = "百相"
            if "择芳" in name:
                attr = "择芳"
            if "展锋" in name:
                attr = "展锋"
            if "揽江" in name:
                attr = "揽江"
            if "灵源" in name:
                attr = "灵源"
            if line["GetType"] == "生活技能":
                attr = "切糕"
            if int(line["MaxStrengthLevel"]) < 6:
                attr = "精简"

            if attr != "":
                resultDict[id] = attr

    with open('equip/resources/Custom_Weapon.tab')as f:

        data_6 = []
        f_csv = csv.reader(f, delimiter='\t')
        headers = next(f_csv)
        print(headers)

        for row in f_csv:
            line = {}
            for i in range(len(row)):
                line[headers[i]] = row[i]
            data_6.append(line)

        for line in data_6:
            if int(line["Level"]) < 4000:
                continue
            name = line["Name"]
            id = "6,%s" % line["ID"]
            attr = ""
            if int(line["MaxStrengthLevel"]) < 6:
                attr = "精简"
            if line["_IsSpecialMagicType"] == "1":
                attr = "特效武器"
            if line["BelongMap"] == "橙武":
                attr = "大橙武"
            if line["BelongMap"] == "奉天证道版本全门派特殊武器升级":
                attr = "门派特效"

            if attr != "":
                resultDict[id] = attr

    with open('equip/resources/Custom_Trinket.tab')as f:

        data_8 = []
        f_csv = csv.reader(f, delimiter='\t')
        headers = next(f_csv)
        print(headers)

        for row in f_csv:
            line = {}
            for i in range(len(row)):
                line[headers[i]] = row[i]
            data_8.append(line)

        for line in data_8:
            if line["Level"] == "" or int(line["Level"]) < 4000:
                continue
            name = line["Name"]
            id = "8,%s" % line["ID"]
            attr = ""
            if line["MaxStrengthLevel"] != "" and int(line["MaxStrengthLevel"]) < 6:
                attr = "精简"
            if line["SkillID"] != "":
                attr = "特效腰坠"

            if attr != "":
                resultDict[id] = attr

    # 读取附魔等级
    enchantDict = {}

    with open('equip/resources/Enchant.tab')as f:
        f_csv = csv.reader(f, delimiter='\t')
        lvl = 0
        for row in f_csv:
            if "铸" in row[1]:  # 紫色铸造
                enchantDict[row[0]] = 2
            elif "甲" in row[1]:  # 蓝色铸造
                enchantDict[row[0]] = 1
            elif "绣" in row[1]:  # 紫色缝纫
                enchantDict[row[0]] = 2
            elif "染" in row[1]:  # 蓝色缝纫
                enchantDict[row[0]] = 1
            elif "鬼晶" in row[1]:  # 吃鸡附魔
                enchantDict[row[0]] = 2
            elif "龙血磨石" in row[1]:
                enchantDict[row[0]] = 2
            elif "残卷" in row[1]:  # 裤子大附魔
                enchantDict[row[0]] = 11
            elif "玉简" in row[1]:  # 裤子大附魔
                enchantDict[row[0]] = 12

    # 读取五彩石等级
    colorDict = {}

    with open('equip/resources/Other.tab')as f:
        f_csv = csv.reader(f, delimiter='\t')
        lvl = 0
        for row in f_csv:
            if "壹" in row[1]:
                colorDict[row[0]] = 1
            elif "贰" in row[1]:
                colorDict[row[0]] = 2
            elif "叁" in row[1]:
                colorDict[row[0]] = 3
            elif "肆" in row[1]:
                colorDict[row[0]] = 4
            elif "伍" in row[1]:
                colorDict[row[0]] = 5
            elif "陆" in row[1]:
                colorDict[row[0]] = 6

    # 输出python文件
    g = open("equip/EquipmentType.py", "w", encoding='utf-8')
    text = """# [Auto-Generated File]
EQUIPMENT_TYPE = %s
ENCHANT_TYPE = %s
COLOR_TYPE = %s"""%(str(resultDict), str(enchantDict), str(colorDict))
    g.write(text)
    g.close()

