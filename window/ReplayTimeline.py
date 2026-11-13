"""Shared personal replay UI: independent mechanism lanes and a fixed skill band."""
import tkinter as tk
from tkinter import font as tkfont

from PIL import Image, ImageDraw, ImageTk

from tools.ResourcePath import get_icon_path
from tools.TimelineLayout import layout_timeline_records


class TimelineIcons(dict):
    """Load only displayed icons; old/missing game icons have a visible fallback."""
    def __init__(self, master):
        super().__init__()
        self.master = master

    def __missing__(self, key):
        try:
            with Image.open(get_icon_path(str(key))) as source:
                image = source.convert('RGBA').resize((20, 20), getattr(Image, 'Resampling', Image).LANCZOS)
        except (OSError, ValueError):
            image = Image.new('RGBA', (20, 20), '#d8d8d8')
            draw = ImageDraw.Draw(image)
            draw.rectangle((0, 0, 19, 19), outline='#777777')
            draw.text((7, 3), '?', fill='#333333')
        self[key] = ImageTk.PhotoImage(image, master=self.master)
        return self[key]


class ReplayTimeline:
    """Keep the original 80px heat/skill/call band visible while mechanisms scroll."""
    def __init__(self, owner, color):
        self.owner = owner
        self.frame = tk.Frame(owner.window, width=730, height=192,
                              highlightthickness=1, highlightbackground=color)
        self.frame.place(x=10, y=460)
        self.canvas = tk.Canvas(self.frame, width=700, height=80,
                                highlightthickness=0, borderwidth=0)
        self.canvas.im = TimelineIcons(self.canvas)
        self.environment = tk.Canvas(self.frame, width=700, height=72,
                                     highlightthickness=0, borderwidth=0, background='white')
        self.environment.place(x=2, y=18)
        self.canvas.place(x=2, y=92)
        self.vertical = tk.Scrollbar(self.frame, orient='vertical', command=self.environment.yview)
        self.vertical.place(x=704, y=18, width=20, height=72)
        self.environment.configure(yscrollcommand=self.vertical.set)
        self.horizontal = tk.Scrollbar(self.frame, orient='horizontal', command=self.scroll_x)
        self.horizontal.place(x=2, y=173, width=722, height=17)
        self.canvas.configure(xscrollcommand=self.horizontal.set)
        self.environment.configure(xscrollcommand=self.horizontal.set)
        self.font = tkfont.nametofont('TkDefaultFont')
        start = owner.result['replay']['startTime']
        self.x_for_time = lambda time: (time-start)/100
        self.label_for = lambda record: str(record.get('skillname', '')) + (
            '*%s' % record['num'] if record.get('num', 1) > 1 else '')
        self.layout = layout_timeline_records(
            owner.result['replay'].get('environment', []), self.x_for_time, self.font.measure,
            label_for_record=self.label_for,
            end_x_for_record=lambda record: max(
                self.x_for_time(record['start']+record.get('duration', 0)),
                self.x_for_time(record['start'])+12+self.font.measure(self.label_for(record))))
        tk.Label(self.frame, text='首领机制 · %d轨（滚轮查看）' % self.layout['laneCount'],
                 anchor='w').place(x=2, y=0, height=18)
        self.environment.bind('<MouseWheel>', self.scroll_environment)
        for canvas in (self.canvas, self.environment):
            canvas.bind('<Shift-MouseWheel>', self.scroll_horizontal)
        owner.replayTimeline = self

    def scroll_x(self, *args):
        self.canvas.xview(*args)
        self.environment.xview(*args)

    def scroll_environment(self, event):
        self.environment.yview_scroll(-int(event.delta/120), 'units')
        return 'break'

    def scroll_horizontal(self, event):
        self.scroll_x('scroll', -int(event.delta/120), 'units')
        return 'break'

    def finish(self):
        # Existing profession renderers draw their personal band at y=30..110.
        # Move those items together; their relative coordinates stay untouched.
        self.canvas.move('all', 0, -30)
        for item in self.layout['items']:
            record, x, y = item['record'], item['x'], item['lane']*24+12
            color = record.get('color') or '#ff7777'
            try:
                self.environment.winfo_rgb(color)
            except tk.TclError:
                color = '#ff7777'
            end = self.x_for_time(record['start']+record.get('duration', 0))
            tags = ('environment', 'environment-%d' % item['index'])
            if end > x:
                # Keep text on white even for dark mechanism colors.
                self.environment.create_rectangle(x, y+8, end, y+11, fill=color, outline='', tags=tags)
            self.environment.create_rectangle(x-11, y-11, x+11, y+11, outline=color, width=2, tags=tags)
            self.environment.create_image(x, y, image=self.canvas.im[record.get('iconid', '')], tags=tags)
            self.environment.create_text(x+12, y-2, text=self.label_for(record), anchor='w',
                                         font=self.font, fill='#111111', tags=tags)
        left = min(0, self.layout['minX'])
        right = max(700, self.owner.result['overall']['sumTime']/100, self.layout['maxX'])
        self.canvas.configure(scrollregion=(left, 0, right, 80))
        self.environment.configure(scrollregion=(left, 0, right, max(72, self.layout['laneCount']*24)),
                                   yscrollincrement=24)
        self.scroll_x('moveto', 0)
        # The other panels are rendered after renderReplay, so place them once
        # the complete window exists instead of changing six unrelated methods.
        self.owner.window.after_idle(self.fit_window)

    def fit_window(self):
        top = self.owner.window
        if not top.winfo_exists():
            return
        panels = []
        extra = 42  # The old replay frame was 150px; the new frame is 192px.
        for child in top.winfo_children():
            info = child.place_info()
            if not info:
                continue
            x, y = int(float(info['x'])), int(float(info['y']))
            if y >= 620:
                y += extra
                child.place_configure(y=y)
            panels.append((child, x, y))
        top.update_idletasks()
        content_height = max((y+child.winfo_height()+10 for child, x, y in panels), default=900)
        screen_width, screen_height = top.winfo_screenwidth(), top.winfo_screenheight()
        height = min(max(900, content_height), max(1, screen_height-80))
        width = min(768 if height < content_height else 750, max(1, screen_width-40))
        top.geometry('%dx%d+%d+%d' % (width, height, max(0, (screen_width-width)//2),
                                     max(0, (screen_height-height-40)//2)))
        if width >= 750 and height >= content_height:
            return
        # Canvas window items may embed sibling widgets: their parent remains
        # the Toplevel, preserving callbacks and all existing panel references.
        outer = tk.Canvas(top, highlightthickness=0, borderwidth=0,
                          scrollregion=(0, 0, 750, content_height))
        outer.place(x=0, y=0, relwidth=1, relheight=1, width=-18, height=-18)
        vertical = tk.Scrollbar(top, orient='vertical', command=outer.yview)
        vertical.place(relx=1, x=-18, y=0, relheight=1, height=-18, width=18)
        horizontal = tk.Scrollbar(top, orient='horizontal', command=outer.xview)
        horizontal.place(x=0, rely=1, y=-18, relwidth=1, width=-18, height=18)
        outer.configure(yscrollcommand=vertical.set, xscrollcommand=horizontal.set)
        for child, x, y in panels:
            child.place_forget()
            outer.create_window(x, y, window=child, anchor='nw')
        outer.bind('<MouseWheel>', lambda event: outer.yview_scroll(-int(event.delta/120), 'units'))
        self.outer = outer
