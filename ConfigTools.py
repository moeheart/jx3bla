# Created by moeheart at 10/10/2020
# 处理config.ini，包括所有选项的解析与导出。

import os
import configparser
from pathlib import Path
import re
import tempfile
import threading
import uuid
import json
import urllib.request

from Constants import EDITION, LVLNAME, LVLTABLE, get_api_url
from tools.Functions import parseEdition


SECTIONS = {
    "general": "General", "actor": "ActorAnalysis", "user": "UserAnalysis",
    "xiangzhi": "XiangZhiAnalysis", "lingsu": "LingSuAnalysis",
    "lijing": "LiJingAnalysis", "butian": "BuTianAnalysis", "yunchang": "YunChangAnalysis",
}
_identity_lock = threading.Lock()
_settings_lock = threading.RLock()


def _read_ini(path):
    parser = configparser.ConfigParser(interpolation=None)
    parser.optionxform = str
    if path.is_file():
        try:
            data = path.read_text(encoding="utf-8-sig")
        except UnicodeDecodeError:
            data = path.read_text(encoding="gbk")
        try:
            parser.read_string(data)
        except configparser.Error as error:
            raise ValueError("配置文件语法不正确，请检查分节和键值。") from error
    return parser


def request_user_uuid():
    mac = "-".join(re.findall(r".{2}", uuid.uuid1().hex[-12:].upper()))
    body = urllib.parse.urlencode({"mac": mac}).encode("utf-8")
    with urllib.request.urlopen(get_api_url("/getUuid"), data=body, timeout=10) as response:
        identifier = json.load(response)["uuid"]
    if not isinstance(identifier, str) or not identifier.strip():
        raise ValueError("服务器未返回用户标识。")
    return identifier


def ensure_user_uuid(config, *, invalid_uuid=None):
    """Called by an online operation in a worker, after the user enabled it."""
    with _identity_lock:
        if config.userUuid and config.userUuid != invalid_uuid:
            return config.userUuid
        existing = Config(config.filename, offline=True)
        if existing.userUuid and existing.userUuid != invalid_uuid:
            config.userUuid = config.item["user"]["uuid"] = existing.userUuid
            config.userId = config.item["user"]["id"] = existing.userId
            return existing.userUuid
        identifier = request_user_uuid()
        updated = {"uuid": identifier}
        if invalid_uuid:
            updated["id"] = ""
        config.saveSettings({"user": updated})
        return identifier

class Config():
    '''
    设置类，负责读取与写入config.ini，并且维护各种设置选项。
    '''
    
    def getUserInfo(self):
        '''
        与服务器通信，获取当前uuid的用户信息并保存在config中。
        '''
        if parseEdition(EDITION) == 0:  # 非联机版本跳过加载步骤
            res = {"item1": 0, "item2": 0, "item3": 0, "item4": 0, "exp": 0, "score": 0, "lvl": 0, "exist": 1}
        else:
            jpost = {'uuid': self.userUuid}
            jparse = urllib.parse.urlencode(jpost).encode('utf-8')
            resp = urllib.request.urlopen(get_api_url('/getUserInfo'), data=jparse)
            res = json.load(resp)
        
        if res['exist'] == 0:
            from tkinter import messagebox
            messagebox.showinfo(title='错误', message='用户唯一标识出错，将重新生成并清除用户数据。如果遇到问题，请联系作者。')
            uuid = self.getNewUuid()
            self.userUuid = uuid
            self.userItems = [0, 0, 0, 0]
            self.exp = 0
            self.score = 0
            self.lvl = 0
            self.item["user"]["uuid"] = uuid
            self.printSettings()
        
        else:
            self.userItems = [res["item1"], res["item2"], res["item3"], res["item4"]]
            self.exp = res["exp"]
            self.score = res["score"]
            self.lvl = res["lvl"]
            
        self.rankNow = LVLNAME[self.lvl]
        self.rankNext = LVLNAME[self.lvl+1]
        self.rankBar = "%d/%d"%(self.exp, LVLTABLE[self.lvl+1])
        
        if self.exp >= LVLTABLE[self.lvl+1]:
            self.rankPercent = 1
        else:
            self.rankPercent = (self.exp - LVLTABLE[self.lvl]) / (LVLTABLE[self.lvl+1] - LVLTABLE[self.lvl])

    def getNewUuid(self):
        '''
        与服务器通信，取得一个新的uuid。
        '''
        return request_user_uuid()

    def initHealerItems(self, items_target, occ):
        '''
        初始化治疗相关的设置.
        params:
        - items_target: 治疗相关的选项列表.
        - occ: 职业描述.
        '''

        items_target["active"] = int(items_target.get("active", 1))
        items_target["speed"] = int(items_target.get("speed", 8780))
        items_target["public"] = int(items_target.get("public", 1))
        items_target["speedforce"] = int(items_target.get("speedforce", 0))
        items_target.pop("stack", None)  # 旧版时间轴显示选项
        if occ == "xiangzhi":
            items_target["caltank"] = int(items_target.get("caltank", 0))
        
    def checkItems(self):
        '''
        检查config.ini是否符合规范，并设置默认选项。
        '''
        try:
            self.item["general"]["playername"] = self.item["general"].get("playername", "")
            self.item["general"]["basepath"] = self.item["general"].get("basepath", "")
            self.item["general"]["jx3path"] = self.item["general"].get("jx3path", "")
            self.item["general"]["mask"] = int(self.item["general"].get("mask", 0))
            self.item["general"]["autoupload"] = int(self.item["general"].get("autoupload", 1))
            self.item["general"]["color"] = int(self.item["general"].get("color", 1))
            self.item["general"]["text"] = int(self.item["general"].get("text", 0))
            self.item["general"]["trivia"] = int(self.item["general"].get("trivia", 0))
            self.item["general"]["datatype"] = self.item["general"].get("datatype", "jcl")
            if self.item["general"]["datatype"] == "jx3dat（已停止支持，非特殊情况勿使用）":
                self.item["general"]["datatype"] = "jx3dat"
            self.item["general"]["edition"] = self.item["general"].get("edition", EDITION)
            self.item["general"]["team"] = self.item["general"].get("team", "")

            self.item["actor"]["active"] = int(self.item["actor"].get("active", 1))
            self.item["actor"]["checkall"] = int(self.item["actor"].get("checkall", 0))
            self.item["actor"]["failthreshold"] = int(self.item["actor"].get("failthreshold", 10))
            # self.item["actor"]["qualifiedrate"] = float(self.item["actor"].get("qualifiedrate", 0.75))
            # self.item["actor"]["alertrate"] = float(self.item["actor"].get("alertrate", 0.85))
            # self.item["actor"]["bonusrate"] = float(self.item["actor"].get("bonusrate", 1.20))
            self.item["actor"]["filter"] = self.item["actor"].get("filter", "")

            self.item["user"]["uuid"] = self.item["user"].get("uuid", "")
            self.item["user"]["id"] = self.item["user"].get("id", "")
            if self.item["user"]["uuid"] == "" and "beta" not in EDITION and not getattr(self, "offline", False):
                uuid = self.getNewUuid()
                self.item["user"]["uuid"] = uuid

            self.initHealerItems(self.item["xiangzhi"], "xiangzhi")
            self.initHealerItems(self.item["lingsu"], "lingsu")
            self.initHealerItems(self.item["lijing"], "lijing")
            self.initHealerItems(self.item["butian"], "butian")
            self.initHealerItems(self.item["yunchang"], "yunchang")

            self.userUuid = self.item["user"].get("uuid", "")
            self.userId = self.item["user"].get("id", "")
            if not self.skipUser and not getattr(self, "offline", False):
                self.getUserInfo()
        except (ValueError, TypeError, KeyError) as error:
            raise ValueError("配置文件中的值不正确，请检查设置内容。") from error

    def printDefault(self):
        '''
        产生默认的config.ini.
        '''
        self.filename.write_text("", encoding="utf-8")
        
    def printSettings(self):
        '''
        将当前设置输出到config.ini。
        '''
        self.saveSettings(self.item)

    def saveSettings(self, changes):
        """Merge edited keys into the latest INI, replacing it only after a complete write."""
        with _settings_lock:
            self._merge_settings(changes)

    def _merge_settings(self, changes):
        parser = _read_ini(self.filename)
        for group in ("xiangzhi", "lingsu", "lijing", "butian", "yunchang"):
            section = SECTIONS[group]
            if parser.has_section(section):
                for key in list(parser[section]):
                    if key.lower() == "stack":
                        parser.remove_option(section, key)
        for group, values in changes.items():
            section = SECTIONS[group]
            if not parser.has_section(section):
                parser.add_section(section)
            spellings = {key.lower(): key for key in parser[section]}
            for key, value in values.items():
                if key != "nameInFile":
                    parser.set(section, spellings.get(key.lower(), key), str(value))
        temporary = None
        try:
            with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=self.filename.parent,
                                             prefix=self.filename.name + ".", delete=False) as output:
                temporary = output.name
                parser.write(output, space_around_delimiters=False)
            os.replace(temporary, self.filename)
        finally:
            if temporary is not None:
                Path(temporary).unlink(missing_ok=True)
        for group, values in changes.items():
            self.item[group].update(values)
        self.userId = self.item["user"]["id"]
        self.userUuid = self.item["user"]["uuid"]

    def loadSettings(self, cf, nameInFile, nameInConfig):
        '''
        从ConfigParser中读取设置内容并转化为pythondict形式.
        params:
        - cf: 用来读取的ConfigParser
        - nameInFile: ConfigParser中的名字.
        - nameInConfig: 本类中保存的名字.
        '''
        if nameInFile in cf.sections():
            self.item[nameInConfig] = {key.lower(): value for key, value in cf.items(nameInFile)}
        else:
            self.item[nameInConfig] = {}
        self.item[nameInConfig]["nameInFile"] = nameInFile

    def __init__(self, filename, build=0, skipUser=1, offline=False):
        '''
        构造方法。
        params
        - filename: 配置文件名，通常为config.ini。
        - skipUser: 是否跳过查找用户信息，默认为是.
        '''
        self.filename = Path(filename).absolute()
        self.offline = offline
        self.item = {}
        self.skipUser = skipUser
        if not self.filename.is_file() and not offline:
            if build:
                self.printDefault()
            else:
                print("config.ini不存在，请检查使用方法，或删除重试。")
            return
        cf = _read_ini(self.filename)
        for group, section in SECTIONS.items():
            self.loadSettings(cf, section, group)
        self.checkItems()
