# Created by moeheart at 08/08/2022
# 评论窗口的实现类.

from window.Window import Window
from window.ToolTip import ToolTip
import hashlib
from tkinter import messagebox
import tkinter as tk
import json
from tools.Functions import *
import urllib.request
from Constants import *

class CommentWindow(Window):
    '''
    评论窗口类。用于维护评论窗口的逻辑。
    '''

    def submit(self):
        '''
        尝试提交评论。
        '''
        result = {}
        result["type"] = int(self.var1.get())
        result["power"] = int(self.var2.get())
        result["content"] = self.commentEntry.get()
        result["pot"] = self.potDescription
        result["server"] = self.server
        result["userid"] = self.userid
        result["mapdetail"] = self.mapDetail
        result["time"] = self.beginTime
        result["player"] = self.targetID

        hashStr = result["server"] + result["player"] + result["userid"] + result["mapdetail"] + str(result["time"])
        hashres = hashlib.md5(hashStr.encode(encoding="utf-8")).hexdigest()

        result["hash"] = hashres

        if result["type"] == 0 or result["power"] == 0:
            messagebox.showinfo(title='错误', message='提交失败，请检查类型与能量是否正确。')
            return

        Jdata = json.dumps(result)
        jpost = {'jdata': Jdata}
        jparse = urllib.parse.urlencode(jpost).encode('utf-8')
        resp = urllib.request.urlopen('http://%s:8009/uploadComment' % IP, data=jparse)
        res = json.load(resp)

        if res['result'] == 'success':
            messagebox.showinfo(title='成功', message='评价成功！')
            self.final()
        elif res['result'] == 'lack':
            messagebox.showinfo(title='失败', message='评价失败，你的积分与能量卡不足以进行此次评价，请尝试使用更低的能量等级。')
        elif res['result'] == 'duplicate':
            messagebox.showinfo(title='失败', message='评价失败，你对该玩家提交过相同的评价。')
        elif res['result'] == 'denied':
            messagebox.showinfo(title='失败', message='评价失败，你的等级无法以使用此功能。')

    def loadWindow(self):
        '''
        使用tkinter绘制复盘窗口。
        '''
        window = tk.Toplevel()
        window.title('评价')
        window.geometry('500x400')

        targetID = self.targetID
        targetColor = getColor(self.targetOcc)
        IDlabel = tk.Label(window, text=targetID, height=1, fg=targetColor)
        IDlabel.grid(row=0, column=0)

        self.var1 = tk.IntVar()

        label1 = tk.Label(window, text="评价类别", height=1)
        label1.grid(row=1, column=0)

        ToolTip(label1, "选取评价类别。点赞会增加目标的信誉分，而吐槽会扣除目标的信誉分。\n在同一场战斗数据中，只能对同一名玩家评价一次。")

        frame1 = tk.Frame(window)
        radio11 = tk.Radiobutton(frame1, text='点赞', variable=self.var1, value=1)
        radio11.grid(row=0, column=0)
        radio12 = tk.Radiobutton(frame1, text='吐槽', variable=self.var1, value=2)
        radio12.grid(row=0, column=1)
        frame1.grid(row=1, column=1)

        self.var2 = tk.IntVar()

        label2 = tk.Label(window, text="评价能量", height=1)
        label2.grid(row=2, column=0)

        frame2 = tk.Frame(window)
        radio21 = tk.Radiobutton(frame2, text='低', variable=self.var2, value=1)
        radio21.grid(row=0, column=1)
        radio22 = tk.Radiobutton(frame2, text='中', variable=self.var2, value=2)
        radio22.grid(row=0, column=2)
        radio23 = tk.Radiobutton(frame2, text='高', variable=self.var2, value=3)
        radio23.grid(row=0, column=3)
        frame2.grid(row=2, column=1)

        ToolTip(label2, "选取评价能量，会影响分数变化的多少。")

        ToolTip(radio21, "使用低能量，分数变化为2，无消耗。")
        ToolTip(radio22, "使用中能量，分数变化为8，消耗中级能量卡或8点积分。")
        ToolTip(radio23, "使用高能量，分数变化为20，消耗高级能量卡或20点积分。")

        potDesLabel = tk.Label(window, text="犯错记录")
        potDesLabel.grid(row=3, column=0)
        potLabel = tk.Label(window, text=self.potDescription)
        potLabel.grid(row=3, column=1, ipadx=75)

        commentDesLabel = tk.Label(window, text="评论内容")
        commentDesLabel.grid(row=4, column=0)
        self.commentEntry = tk.Entry(window, show=None, width=50)
        self.commentEntry.grid(row=4, column=1, ipady=25)

        submitButton = tk.Button(window, text='提交', command=self.submit)
        submitButton.grid(row=5, column=1)

        self.window = window
        window.protocol('WM_DELETE_WINDOW', self.final)

    def __init__(self, id, occ, pots, server, userid, mapDetail, beginTime):
        super().__init__()
        self.targetID = id
        self.targetOcc = occ
        self.potDescription = pots
        self.server = server
        self.userid = userid
        self.mapDetail = mapDetail
        self.beginTime = beginTime