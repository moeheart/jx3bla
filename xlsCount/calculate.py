import os
import json
import csv

l = os.listdir('.')

playerSkillDict = {}
headerDict = {}

for file in l:
    if file[-1] != 't':
        continue
    f = open(file, "r")
    s = f.read()
    s = s.strip('\n')
    s = s.replace("'", '"')
    d = json.loads(s)
    for player in d:
        if player not in playerSkillDict:
            playerSkillDict[player] = {}
        for skill in d[player]:
            if skill not in playerSkillDict[player]:
                playerSkillDict[player][skill] = 0
                headerDict[skill] = 0
            playerSkillDict[player][skill] += d[player][skill]
    #if d["左渭雨@飞鸢泛月"]["寂灭成功格挡"] > d["左渭雨@飞鸢泛月"]["寂灭总计次数"]:
    #    print(file)

headers = [''] + list(headerDict.keys())
rows = []
for player in playerSkillDict:
    row = [player]
    for skill in playerSkillDict[player]:
        row.append(playerSkillDict[player][skill])
    rows.append(row)

with open('result.csv','w',encoding='utf-8', newline='') as f:
    f_csv = csv.writer(f)
    f_csv.writerow(headers)
    f_csv.writerows(rows)

