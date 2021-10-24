# Created by moeheart at 10/24/2021
# 生成器的生成器，用于将部分常量文件打包到一个python文件中输出。
# 这样在打包之后位置主程序只有一个exe，与现在的发布形式一致。

import os

if __name__ == "__main__":
    # 数据准备
    pathDict = ['icons']  # 打包icons下的全部文件
    fileDict = {}

    l = os.listdir('icons')
    for line in l:
        fileName = 'icons/%s'%line
        f = open(fileName, "rb")
        content = f.read()
        fileDict[fileName] = content
        f.close()

    # 输出python文件

    g = open("GenerateFiles.py", "w")
    header = """# [Auto-Generated File]
import os

def checkAndWriteFiles():

    paths = %s
    for pathname in paths:
        if os.path.exists(pathname):
            pass
        else:
            os.mkdir(pathname)
    
    files = {\n"""%(str(pathDict))
    g.write(header)
    for key in fileDict:
        line = '        "%s": %s,\n'%(key, fileDict[key])
        g.write(line)
    ending = """    }
    
    for filename in files:
        if os.path.exists(filename):
            pass
        else:
            f = open(filename, "wb")
            f.write(files[filename])
            f.close()
"""
    g.write(ending)
    g.close()

