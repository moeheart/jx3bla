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

    # 输出python文件
    g = open("replayer/Name.py", "w", encoding='utf-8')
    text = """# [Auto-Generated File]
SKILL_NAME = %s"""%(str(resultDict))
    g.write(text)
    g.close()

