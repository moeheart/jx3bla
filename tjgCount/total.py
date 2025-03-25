import os
import json
import xlwt
from data import *

l = os.listdir(".")

def write_excel(sheet, data, headers):
    i = 0
    j = 0
    for header in headers:
        j += 1
        sheet.write(i, j, header)
    for player in data:
        i += 1
        j = 0
        sheet.write(i, j, player)
        for key in headers:
            j += 1
            sheet.write(i, j, data[player].get(key, 0))

def dictadd(x, y):
    for key in y:
        if key in x:
            x[key] += y[key]
        else:
            x[key] = y[key]
    return x

headers = HEADER

playerNickname = {}
playerActualname = {}

with open("name_list.txt", "r", encoding="utf-8") as f:
    s = f.read()
    d = s.strip('\n').split('\n')
    for line in d:
        name0 = line.split(' ')[0]
        name1 = line.split(' ')[1]
        if name1 not in playerNickname:
            playerNickname[name1] = []
        playerNickname[name1].append(name0)
        playerActualname[name0] = name1

for name0 in playerActualname:
    name1 = playerActualname[name0]
    full_name = "%s(%s)" % (name1, ','.join(playerNickname[name1]))
    playerActualname[name0] = full_name

for name1 in playerNickname:
    full_name = "%s(%s)" % (name1, ','.join(playerNickname[name1]))
    playerActualname[name1] = full_name

workbook = xlwt.Workbook(encoding="utf-8")
sheet0 = workbook.add_sheet("汇总")

overall_result = {"描述": {"力": "造成的rDPS越高，本项得分越高。对每天出勤的每个BOSS独立判定，并以当天团队的rDPS最大值为上限。（TN记为4.0）",
                         "速": "普通机制的命中次数越少，本项得分越高。对每天出勤的每个机制独立判定，并以当天团队的命中最大值为上限。",
                         "敏": "严重/致死机制的命中次数越少，本项得分越高。对每天出勤的每个机制独立判定，并以当天团队的命中最大值为上限。",
                         "智": "前期机制的命中次数越少，本项得分越高。对每天出勤的每个机制独立判定，并以当天团队的命中最大值为上限，每天递减40%。",
                         "体": "出勤时间越长，本项得分越高。以全部时间的总和为上限。注意躺尸的时间不算作出勤时间。",
                         }}

scoreCount = {}
scoreSum = {}

zhiCoeff = 1

for file in l:
    if not os.path.isdir(file):
        continue
    file2 = "%s/result.log" % file
    if not os.path.exists(file2):
        continue
    sheet = workbook.add_sheet(file)
    with open(file2, "r", encoding='utf-8') as f:
        j = f.read().replace("'", '"')
        data = json.loads(j)

        print(playerActualname)

        dataT = {}
        for key in data:
            name = playerActualname.get(key, key)
            if name not in dataT:
                dataT[name] = data[key].copy()
            else:
                dataT[name] = dictadd(dataT[name], data[key])

        print(dataT.keys())

        write_excel(sheet, dataT, headers)

        maxValue = {}
        maxScore = {}

        for key in headers:
            maxValue[key] = 0
            for player in dataT:
                value = dataT[player].get(key, 0)
                if value > maxValue[key]:
                    maxValue[key] = value

                if player not in scoreCount:
                    scoreCount[player] = {
                        "力": 0,
                        "速": 0,
                        "敏": 0,
                        "智": 0,
                        "体": 0,
                    }
                    scoreSum[player] = {
                        "力": 0,
                        "速": 0,
                        "敏": 0,
                        "智": 0,
                        "体": 0,
                    }

        for key in headers:
            num = int(key[0])
            maxScore = 0
            scoreData = {}
            for player in dataT:
                time = dataT[player].get("%d号时间" % num, 0)
                value = dataT[player].get(key, 0)
                score = 0
                if maxValue[key] != 0 and time != 0:
                    score = value / maxValue[key] / time
                scoreData[player] = score
                if score > maxScore:
                    maxScore = score

            for player in dataT:
                time = dataT[player].get("%d号时间" % num, 0)
                # print(time, key, maxScore)
                if time == 0 and "时间" not in key:
                    continue
                if maxScore == 0:
                    continue
                finalScore = 1 - scoreData[player] / maxScore
                if HEADER[key] == 0:
                    scoreCount[player]["速"] += finalScore
                    scoreSum[player]["速"] += 1
                    scoreCount[player]["智"] += zhiCoeff * finalScore
                    scoreSum[player]["智"] += zhiCoeff
                elif HEADER[key] == 1:
                    scoreCount[player]["敏"] += finalScore
                    scoreSum[player]["敏"] += 1
                    scoreCount[player]["智"] += zhiCoeff * finalScore
                    scoreSum[player]["智"] += zhiCoeff
                elif "rDPS" in key:
                    scoreCount[player]["力"] += dataT[player].get(key, 0)
                    if dataT[player].get(key, 0) == 0:
                        scoreCount[player]["力"] += 0.8 * maxValue[key]
                    scoreSum[player]["力"] += maxValue[key]
                elif "时间" in key:
                    scoreCount[player]["体"] += dataT[player].get(key, 0)
                    scoreSum[player]["体"] += maxValue[key]
    zhiCoeff *= 0.6

maxSumTi = 0
for player in scoreCount:
    if scoreSum[player]["体"] > maxSumTi:
        maxSumTi = scoreSum[player]["体"]

for player in scoreCount:
    scoreSum[player]["体"] = maxSumTi

player_result = []

for player in scoreCount:
    line = {"player": player, "sum": 0}
    for key in scoreCount[player]:
        if scoreSum[player][key] != 0:
            line[key] = int(scoreCount[player][key] / scoreSum[player][key] * 500) / 100
            line["sum"] += float(line[key])
        else:
            line[key] = 0
    player_result.append(line)

# print(scoreSum)
# print(scoreCount)

player_result.sort(key=lambda x:-x["sum"])

for line in player_result:
    overall_result[line["player"]] = {
        "力": line["力"],
        "速": line["速"],
        "敏": line["敏"],
        "智": line["智"],
        "体": line["体"],
    }

# print(players)
write_excel(sheet0, overall_result, ["力", "速", "敏", "智", "体"])

workbook.save("output.xls")


# 力：造成的rDPS越高，本项得分越高。对每天出勤的每个BOSS独立判定，并以当天团队的rDPS最大值为上限。（TN记为平均分）
# 速：普通机制的命中次数越少，本项得分越高。对每天出勤的每个机制独立判定，并以当天团队的命中最大值为上限。
# 敏：严重/致死机制的命中次数越少，本项得分越高。对每天出勤的每个机制独立判定，并以当天团队的命中最大值为上限。
# 智：前期机制的命中次数越少，本项得分越高。对每天出勤的每个机制独立判定，并以当天团队的命中最大值为上限，每天递减40%。
# 体：出勤时间越长，本项得分越高。以全部时间的总和为上限。注意躺尸的时间不算作出勤时间。
