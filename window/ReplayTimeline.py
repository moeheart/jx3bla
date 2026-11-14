"""Shared personal replay UI: independent mechanism lanes and a fixed skill band."""
import tkinter as tk
from tkinter import font as tkfont
from tkinter import ttk

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
        self.font = tkfont.nametofont('TkDefaultFont')
        self.lane_height = max(24, self.font.metrics('linespace')+6)
        header_height = max(18, self.font.metrics('linespace')+1)
        # At larger UI scales, leave the skill band and its scrollbar on screen
        # even if that means initially showing fewer environment lanes.
        environment_height = min(self.lane_height*3, max(self.lane_height,
            owner.window.winfo_screenheight()-80-18-460-header_height-80-22))
        skill_y = header_height+environment_height+2
        self.frame_height = skill_y+100
        self.frame = tk.Frame(owner.window, width=730, height=self.frame_height,
                              highlightthickness=1, highlightbackground=color)
        self.frame.place(x=10, y=460)
        self.canvas = tk.Canvas(self.frame, width=700, height=80,
                                highlightthickness=0, borderwidth=0)
        self.canvas.im = TimelineIcons(self.canvas)
        self.environment = tk.Canvas(self.frame, width=700, height=environment_height,
                                     highlightthickness=0, borderwidth=0, background='white')
        self.environment.place(x=2, y=header_height)
        self.canvas.place(x=2, y=skill_y)
        self.vertical = tk.Scrollbar(self.frame, orient='vertical', command=self.environment.yview)
        self.vertical.place(x=704, y=header_height, width=20, height=environment_height)
        self.environment.configure(yscrollcommand=self.vertical.set)
        self.horizontal = ttk.Scrollbar(self.frame, orient='horizontal', command=self.scroll_x)
        self.horizontal.place(x=2, y=skill_y+81, width=722, height=17)
        self.canvas.configure(xscrollcommand=self.horizontal.set)
        self.environment.configure(xscrollcommand=self.horizontal.set)
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
                 anchor='w').place(x=2, y=0, height=header_height)
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
            record, x, y = item['record'], item['x'], item['lane']*self.lane_height+self.lane_height/2
            color = record.get('color') or '#ff7777'
            try:
                self.environment.winfo_rgb(color)
            except tk.TclError:
                color = '#ff7777'
            end = self.x_for_time(record['start']+record.get('duration', 0))
            tags = ('environment', 'environment-%d' % item['index'])
            if end > x:
                # Keep text on white even for dark mechanism colors.
                self.environment.create_rectangle(x, y+self.lane_height/2-4, end,
                                                   y+self.lane_height/2-1, fill=color, outline='', tags=tags)
            self.environment.create_rectangle(x-11, y-11, x+11, y+11, outline=color, width=2, tags=tags)
            self.environment.create_image(x, y, image=self.canvas.im[record.get('iconid', '')], tags=tags)
            self.environment.create_text(x+12, y-2, text=self.label_for(record), anchor='w',
                                         font=self.font, fill='#111111', tags=tags)
        left = min(0, self.layout['minX'])
        right = max(700, self.owner.result['overall']['sumTime']/100, self.layout['maxX'])
        self.canvas.configure(scrollregion=(left, 0, right, 80))
        self.environment.configure(scrollregion=(left, 0, right, max(
            int(self.environment.cget('height')), self.layout['laneCount']*self.lane_height)),
            yscrollincrement=self.lane_height)
        self.scroll_x('moveto', 0)

    def fit_window(self):
        """Finalize once, synchronously after every personal panel is constructed.

        Never schedule this from renderReplay: Tk may process idle callbacks
        before renderTeam/renderRate/renderAdvertise have created their frames.
        """
        top = self.owner.window
        if getattr(self, '_window_fitted', False) or not top.winfo_exists():
            return
        self._window_fitted = True
        panels = []
        extra = self.frame_height-150
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
        content_width = max((x+child.winfo_width()+10 for child, x, y in panels), default=750)
        screen_width, screen_height = top.winfo_screenwidth(), top.winfo_screenheight()
        height = min(max(900, content_height), max(1, screen_height-80))
        width = min(content_width+(18 if height < content_height else 0), max(1, screen_width-40))
        top.geometry('%dx%d+%d+%d' % (width, height, max(0, (screen_width-width)//2),
                                     max(0, (screen_height-height-40)//2)))
        # Canvas window items may embed sibling widgets: their parent remains
        # the Toplevel, preserving callbacks and all existing panel references.
        # Keep this container at every screen size so later shrinking the
        # window cannot leave the footer or horizontal timeline bar unreachable.
        outer = tk.Canvas(top, highlightthickness=0, borderwidth=0)
        outer.grid(row=0, column=0, sticky='nsew')
        top.rowconfigure(0, weight=1)
        top.columnconfigure(0, weight=1)
        vertical = tk.Scrollbar(top, orient='vertical', command=outer.yview)
        horizontal = tk.Scrollbar(top, orient='horizontal', command=outer.xview)
        outer.configure(yscrollcommand=vertical.set, xscrollcommand=horizontal.set)
        items = []
        for child, x, y in panels:
            child.place_forget()
            items.append((outer.create_window(x, y, window=child, anchor='nw'), x, y))
            # Embedded siblings retain their native stacking order; the new
            # Canvas otherwise covers them and intercepts their mouse input.
            child.lift(outer)

        def resize_window(event):
            if event.widget != top:
                return
            need_vertical = event.height < content_height
            need_horizontal = event.width-(vertical.winfo_reqwidth() if need_vertical else 0) < content_width
            need_vertical = event.height-(horizontal.winfo_reqheight() if need_horizontal else 0) < content_height
            need_horizontal = event.width-(vertical.winfo_reqwidth() if need_vertical else 0) < content_width
            if need_vertical:
                vertical.grid(row=0, column=1, sticky='ns')
            else:
                vertical.grid_remove()
                outer.yview_moveto(0)
            if need_horizontal:
                horizontal.grid(row=1, column=0, sticky='ew')
            else:
                horizontal.grid_remove()
                outer.xview_moveto(0)

        def place_panels(event):
            if event.widget != outer:
                return
            offset = max(0, (event.width-content_width)//2)
            for item, x, y in items:
                outer.coords(item, x+offset, y)
            outer.configure(scrollregion=(0, 0, max(content_width, event.width),
                                           max(content_height, event.height)))

        top.bind('<Configure>', resize_window, add='+')
        outer.bind('<Configure>', place_panels, add='+')
        outer.bind('<MouseWheel>', lambda event: outer.yview_scroll(-int(event.delta/120), 'units'))
        self.outer = outer
        self.outer_vertical = vertical
        self.outer_horizontal = horizontal
