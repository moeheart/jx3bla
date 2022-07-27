# Created by moeheart at 11/14/2021
# 技能名称生成器，用于从解包生成各种技能和buff的名称。

import os
import csv

if __name__ == "__main__":
    # 数据准备
    resultDict = {}

    # 读取buff
    with open('equip/resources/buff.txt')as f:

        f_csv = csv.reader(f, delimiter='\t')
        headers = next(f_csv)
        print(headers)

        for row in f_csv:
            s = "2,%s,%s"%(row[0], row[1])
            resultDict[s] = row[7]

    # 读取技能
    with open('equip/resources/skill.txt')as f:

        f_csv = csv.reader(f, delimiter='\t')
        headers = next(f_csv)
        print(headers)

        for row in f_csv:
            s = "1,%s,%s"%(row[0], row[1])
            resultDict[s] = row[10]

    # 读取buff是否有化解和减伤属性
    absorbDict = {}
    resistDict = {}
    with open('equip/resources/buff.tab')as f:

        f_csv = csv.reader(f, delimiter='\t')
        headers = next(f_csv)
        print(headers)

        for row in f_csv:
            s = "2,%s,%s" % (row[0], row[9])
            hasAbsorb = 0
            resistValue = 0
            for i in range(27, 82, 3):
                if i > len(row):
                    break
                if "Absorb" in row[i] and "Only" not in row[i] and "Therapy" not in row[i]:
                    hasAbsorb = 1
                if "atGlobalResistPercent" in row[i] and row[i+1] != "":
                    resistValue = int(float(row[i+1]))
                if "DamageCoefficient" in row[i] and int(float(row[i+1])) < 0 and row[i+1] != "":
                    resistValue = -int(float(row[i+1]))
            if hasAbsorb:
                absorbDict[s] = 1
            if resistValue != 0:
                resistDict[s] = resistValue
                # print(s)

    # 输出python文件
    g = open("replayer/Name.py", "w", encoding='utf-8')
    text = """# [Auto-Generated File]
SKILL_NAME = %s
ABSORB_DICT = %s
RESIST_DICT = %s""" % (str(resultDict), str(absorbDict), str(resistDict))
    g.write(text)
    g.close()

