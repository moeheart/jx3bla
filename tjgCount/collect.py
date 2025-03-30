import os
import json
import csv
from data import *

header = HEADER
headers = ['']

for key in HEADER:
    headers.append(key)

l = os.listdir('.')

playerSkillDict = {}
playerTimeDict = {}

NAME = {}

with open("name_list.txt", "r", encoding="utf-8") as f:
    s = f.read()
    s = s.strip('\n')
    l2 = s.split('\n')
    for line in l2:
        ll = line.split(' ')
        NAME[ll[0]] = ll[1]

# print(NAME)

for file in l:
    if file[-1] != 't':
        continue
    if file == "name_list.txt":
        continue
    f = open(file, "r", encoding="utf-8")
    s = f.read()
    s = s.strip('\n')
    s = s.replace("'", '"')
    d = json.loads(s)
    for player_raw in d:
        player = player_raw
        if player in NAME:
            player = NAME[player]
        largest = 0
        if player not in playerSkillDict:
            playerSkillDict[player] = {}
            playerTimeDict[player] = 0
            for key in header:
                playerSkillDict[player][key] = 0

        for skill in d[player_raw]:
            if skill not in playerSkillDict[player]:
                playerSkillDict[player][skill] = 0
            if "时间" in skill:
                playerTimeDict[player] = d[player_raw][skill]
            if "rDPS" in skill:
                # print(d)
                # print(playerSkillDict)
                # print(playerTimeDict)
                # print(player)
                # print(skill)
                # print(d[player][skill])
                # print(playerSkillDict[player][skill])
                # print(playerTimeDict[player])
                if d[player_raw][skill] > playerSkillDict[player][skill] and playerTimeDict[player] > 90:
                    playerSkillDict[player][skill] = d[player_raw][skill]
            else:
                playerSkillDict[player][skill] += d[player_raw][skill]

rows = []
for player in playerSkillDict:
    row = [player]
    for skill in playerSkillDict[player]:
        row.append(playerSkillDict[player][skill])
    rows.append(row)
with open('result.csv', 'w', encoding='utf-8', newline='') as f:
    f_csv = csv.writer(f)
    f_csv.writerow(headers)
    f_csv.writerows(rows)

with open('result.log', 'w', encoding='utf-8') as f:
    f.write(str(playerSkillDict))