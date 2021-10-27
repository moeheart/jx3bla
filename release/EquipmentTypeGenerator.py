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

    # 输出python文件

    g = open("equip/EquipmentType.py", "w")
    text = """# [Auto-Generated File]
EQUIPMENT_TYPE = %s"""%str(resultDict)
    g.write(text)
    g.close()

