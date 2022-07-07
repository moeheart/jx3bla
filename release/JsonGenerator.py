# Created by moeheart at 06/30/2022
# json常量文件的生成器，用于生成存有json常量的python文件用于导入。

import os

if __name__ == "__main__":
    # 数据准备

    with open("replayer/occ/Review.json", "r", encoding="utf-8") as f:
        s = f.read()

    pathDict = ['icons']  # 打包icons下的全部文件
    fileDict = {}

    # 输出python文件

    with open("tools/StaticJson.py", "w", encoding="utf-8") as g:
        content = """# [Auto-Generated File]
REVIEW_JSON = %s""" % s
        g.write(content)

