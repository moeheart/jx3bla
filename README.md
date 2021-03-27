# 剑三警长(原剑网三战斗日志分析、奶歌复盘)

JX3 **B**attle **L**og **A**nalyser v6.3.0

用于深入分析剑网三中茗伊战斗复盘的框架。

支持奶歌的复盘，与演员的复盘。

具体功能还在不断完善中，为了效率可能会做出一些妥协，不慌。

## 使用方法1

在剑网三安装目录中的`JX3\bin\zhcn_hd\interface\MY#DATA\(一串数字)@zhcn\userdata\fight_stat`下找到战斗记录，将战斗记录放在本目录下。

运行：

`python3 MainWindow.py`

其中，每个数字对应了唯一的角色ID，但具体的文件夹要通过猜测来获得。

## 使用方法2

在`config.ini`中填写**记录者**的角色名（并不一定是奶歌的角色名）。然后运行：

`python3 MainWindow.py`

其会自动寻找对应角色的最后一次战斗记录。

## 发布

`pyinstaller -F -i jx3bla.ico MainWindow.py`

## 联系作者

QQ群：418483739


