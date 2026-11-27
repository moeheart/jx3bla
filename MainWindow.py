"""Desktop entry point and the network protocol used by replay sessions."""
import http.client
import json
import sys
import urllib.parse
import urllib.request

from Constants import EDITION, get_api_url


def get_upload_timeout(payload_bytes):
    """Budget a combined form at 16 KiB/s plus 60 seconds for its response.

    urllib applies this one timeout to blocking socket operations, not to a
    separate connection/read phase or the total transaction. Keep it bounded.
    """
    transfer_seconds = (payload_bytes + 16 * 1024 - 1) // (16 * 1024)
    return min(600, max(120, transfer_seconds + 60))


class MainWindow:
    """Upload queue shared by the desktop analysis session and protocol callers."""

    def __init__(self, notice=None):
        self.uploadData = []
        self.notice = notice

    def setNotice(self, update):
        if self.notice:
            self.notice(update)

    def loadWindow(self):
        from window.QtDesktop import run
        return run()

    def addUploadData(self, uploadData):
        '''
        增加一个需要上传的数据.
        '''
        n = len(self.uploadData)
        uploadData["id"] = n
        self.uploadData.append(uploadData)

    def executeUploadData(self):
        '''
        执行数据上传.
        '''

        if "beta" in EDITION:
            return
        if not self.uploadData:
            self.setNotice({"t1": "没有待上传的记录。", "c1": "#000000",
                            "t2": "请先分析一场已通关的战斗。", "c2": "#000000"})
            return

        actualData = {"data": []}
        for line in self.uploadData:
            singleData = {"type": line["type"], "data": line["data"], "id": line["id"]}
            actualData["data"].append(singleData)

        # return
        self.setNotice({"t1": "正在上传数据……", "c1": "#000000"})

        Jdata = json.dumps(actualData)
        jpost = {'jdata': Jdata}
        jparse = urllib.parse.urlencode(jpost).encode('utf-8')
        try:
            with urllib.request.urlopen(get_api_url('/uploadCombinedData'), data=jparse,
                                        timeout=get_upload_timeout(len(jparse))) as resp:
                res = json.load(resp)
            if not isinstance(res, dict) or res.get("status") not in ("success", "fail"):
                raise ValueError("Invalid upload response")
            if res["status"] == "success":
                records = res.get("data")
                if not isinstance(records, list) or len(records) != len(self.uploadData):
                    raise ValueError("Incomplete upload response")
                for pending, record in zip(self.uploadData, records):
                    if not isinstance(record, dict):
                        raise ValueError("Invalid upload result")
                    if pending["type"] == "replay":
                        required = {"result"} if record.get("result") == "fail" else {"result", "shortID", "num", "scoreRank"}
                    else:
                        required = {"scoreStatus", "scoreAdd"} if record.get("scoreStatus") == "success" else {"scoreStatus"}
                    if not required.issubset(record):
                        raise ValueError("Incomplete upload result")
        except (OSError, ValueError, http.client.HTTPException):
            self.setNotice({"t1": "上传数据失败。", "c1": "#ff0000",
                            "t2": "待上传记录已保留，请稍后重试。", "c2": "#000000"})
            return

        # print("[res]", res)

        # 解析返回的数据

        if res["status"] == "fail":
            self.setNotice({"t1": "上传数据失败。", "c1": "#ff0000",
                            "t2": "待上传记录已保留，请稍后重试。", "c2": "#000000"})
            return
        else:
            for i in range(len(self.uploadData)):
                if self.uploadData[i]["type"] == "replay":
                    # 复盘. 需要更新复盘编号.
                    if res["data"][i]["result"] != "fail":
                        self.uploadData[i]["anchor"]["overall"]["shortID"] = res["data"][i]["shortID"]
                        self.uploadData[i]["anchor"]["overall"]["numReplays"] = res["data"][i]["num"]
                        self.uploadData[i]["anchor"]["overall"]["scoreRank"] = res["data"][i]["scoreRank"]
                    else:
                        self.uploadData[i]["anchor"]["overall"]["shortID"] = "数据保存出错"
                elif self.uploadData[i]["type"] == "battle":
                    self.setNotice({"t2": "战斗记录已提交。", "c2": "#14695f"})

        # 清空上传数据
        self.uploadData = []


if __name__ == "__main__":
    if "--release-smoke-test" in sys.argv:
        from release.SmokeTest import main
        main()
    elif "--validate-desktop" in sys.argv:
        from tools.ValidateDesktop import main
        main()
    else:
        from window.QtDesktop import run
        raise SystemExit(run())
