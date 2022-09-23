import os
import json
import csv

l = os.listdir('.')

playerSkillDict = {}
headerDict = {}

rows = []

for file in l:
    if file[-1] != 't':
        continue
    f = open(file, "r")
    s = f.read()
    s = s.strip('\n')
    s = s.replace("'", '"')
    d = json.loads(s)
    row = [file.split('.')[0]]
    for key in d:
        headerDict[key] = 0
        row.append(d[key])
    rows.append(row)

headers = ['时间'] + list(headerDict.keys())

with open('result.csv','w',encoding='utf-8', newline='') as f:
    f_csv = csv.writer(f)
    f_csv.writerow(headers)
    f_csv.writerows(rows)

