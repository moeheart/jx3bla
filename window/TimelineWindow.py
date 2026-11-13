# Created by moeheart at 04/14/2022
# 时间轴窗口类文件.

import tkinter as tk
import os
from PIL import Image
from PIL import ImageTk
from tools.Functions import *
import threading
import pyperclip
from tkinter import messagebox
from window.Window import Window
from tools.ResourcePath import get_icon_dir, get_icon_path

class TimelineWindow(Window):
    '''
    时间轴窗口的展示类.
    '''

    def shouldShowTimelineRecord(self, record):
        return record.get("iconid", "") != "341"

    def generateLinear(self):
        '''
        生成线性时间轴.
        '''
        try:
            startSec = float(self.entry.get())
        except:
            startSec = 0.0
        res = ""
        for line in self.bh.log["environment"]:
            if not self.shouldShowTimelineRecord(line):
                continue
            time = (line["start"] - self.bh.startTime) / 1000
            if startSec > time:
                continue
            timeS = "%.1f" % (time - startSec)
            text = "%s,%s;\n" % (timeS, line["skillname"])
            res += text
        pyperclip.copy(res)
        messagebox.showinfo(title='提示', message='导出到剪贴板成功！')

    def generateParallel(self):
        '''
        生成双排时间轴.
        '''
        try:
            startSec = float(self.entry.get())
        except:
            startSec = 0.0
        res1 = ""
        res2 = ""
        n = 0
        for line in self.bh.log["environment"]:
            if not self.shouldShowTimelineRecord(line):
                continue
            time = (line["start"] - self.bh.startTime) / 1000
            if startSec > time:
                continue
            timeS = "%.1f" % (time - startSec)
            text = "%s,%s;" % (timeS, line["skillname"])
            if n % 2 == 0:
                res1 += text
            else:
                res2 += text
            n += 1
        res = "%s\n%s\n" % (res1, res2)
        pyperclip.copy(res)
        messagebox.showinfo(title='提示', message='导出到剪贴板成功！')


    def loadWindow(self):
        """Draw exact-time anchors in measured lanes, with scrollable minutes."""
        import tkinter.font as tkfont
        from tools.TimelineLayout import layout_timeline_records

        window = tk.Toplevel()
        window.title('时间轴 · %s' % self.boss)
        self.window = window
        window.geometry('960x%d' % min(720, max(400, window.winfo_screenheight() - 120)))
        window.minsize(620, 340)
        footer = tk.Frame(window)
        footer.pack(side='bottom', fill='x', padx=12, pady=8)
        tk.Label(footer, text='起始时间：').grid(row=0, column=0)
        self.entry = tk.Entry(footer, width=12)
        self.entry.insert(0, '0')
        self.entry.grid(row=0, column=1, padx=(0, 12))
        tk.Button(footer, text='生成线性时间轴', command=self.generateLinear).grid(row=0, column=2)
        tk.Button(footer, text='生成双排时间轴', command=self.generateParallel).grid(row=0, column=3)
        frame = tk.Frame(window)
        frame.pack(fill='both', expand=True, padx=10, pady=(10, 0))
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        canvas = tk.Canvas(frame, background='white', highlightthickness=0)
        canvas.grid(row=0, column=0, sticky='nsew')
        vertical = tk.Scrollbar(frame, orient='vertical', command=canvas.yview)
        vertical.grid(row=0, column=1, sticky='ns')
        horizontal = tk.Scrollbar(frame, orient='horizontal', command=canvas.xview)
        horizontal.grid(row=1, column=0, sticky='ew')
        canvas.configure(yscrollcommand=vertical.set, xscrollcommand=horizontal.set)
        self.canvas = canvas
        font = tkfont.nametofont('TkDefaultFont')
        duration = max(0, self.bh.finalTime - self.bh.startTime)
        minute_count = duration // 60000 + 1
        records = [[] for _ in range(minute_count)]
        for record in self.bh.log['environment']:
            offset = record['start'] - self.bh.startTime
            if self.shouldShowTimelineRecord(record) and 0 <= offset <= duration:
                records[offset // 60000].append(record)
        seconds = lambda record: '%.1f' % ((record['start'] - self.bh.startTime) / 1000)
        self.layoutRows = []
        for minute, row in enumerate(records):
            base_time = self.bh.startTime + minute * 60000
            layout = layout_timeline_records(row, lambda time, base=base_time: (time-base)*.012,
                                             font.measure, secondary_for_record=seconds)
            self.layoutRows.append(layout)
        origin = 20 - min(0, min((row['minX'] for row in self.layoutRows), default=0))
        width = origin + max(720, max((row['maxX'] for row in self.layoutRows), default=0)) + 20
        canvas.im = {}
        for identifier in {record['iconid'] for row in records for record in row}:
            path = get_icon_path(identifier)
            if os.path.isfile(path):
                try:
                    with Image.open(path) as source:
                        canvas.im[identifier] = ImageTk.PhotoImage(source.resize((20, 20), Image.LANCZOS))
                except (OSError, ValueError):
                    pass
        canvas.recordItems = []
        y = 12
        for minute, layout in enumerate(self.layoutRows):
            extent = min(60000, max(0, duration-minute*60000)) * .012
            canvas.create_line(origin, y+12, origin+extent, y+12, fill='#94a3b8', width=2)
            for second in range(0, int(extent/.012/1000)+1, 10):
                x = origin+second*12
                canvas.create_line(x, y+8, x, y+16, fill='#94a3b8')
                canvas.create_text(x, y-1, text='%d:%02d' % (minute, second),
                                   font=font, fill='#64748b')
            for item in layout['items']:
                record = item['record']
                x, base_y = origin+item['x'], y+32+item['lane']*58
                color = record.get('color') or '#334155'
                try:
                    canvas.winfo_rgb(color)
                except tk.TclError:
                    color = '#334155'
                label = canvas.create_text(x, base_y, text=record['skillname'],
                                           font=font, fill=color, tags=('timeline-label',))
                if record['iconid'] in canvas.im:
                    canvas.create_image(x, base_y+20, image=canvas.im[record['iconid']])
                else:
                    canvas.create_oval(x-7, base_y+13, x+7, base_y+27, fill=color, outline='')
                clock = canvas.create_text(x, base_y+40, text=seconds(record), font=font,
                                           fill=color, tags=('timeline-time',))
                canvas.recordItems.append(dict(record=record, lane=item['lane'], minute=minute,
                                               x=x, label=label, clock=clock))
            y += 38 + max(1, layout['laneCount'])*58
        canvas.configure(scrollregion=(0, 0, width, y+12))
        canvas.bind('<MouseWheel>', lambda event: canvas.yview_scroll(-int(event.delta/120), 'units'))
        canvas.bind('<Shift-MouseWheel>', lambda event: canvas.xview_scroll(-int(event.delta/120), 'units'))
        window.protocol('WM_DELETE_WINDOW', self.final)

    def setData(self, bh, boss):
        '''
        导入数据.
        params:
        - bh: 战斗流程信息，与BattleLog中的定义相同.
        - boss: BOSS名称.
        '''
        self.bh = bh
        self.boss = boss

    def __init__(self):
        super().__init__()
