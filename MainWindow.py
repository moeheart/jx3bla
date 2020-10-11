import tkinter as tk
import threading
from main import replay_by_window

from FileLookUp import FileLookUp
from ConfigTools import Config
from LiveBase import LiveListener

window = tk.Tk()
window.title('剑三警长')
window.geometry('300x200')

var = tk.StringVar()

l = tk.Label(window, text='剑三警长', font=('Arial', 24), width=30, height=2)
l.pack()

def replay():
    replay_by_window()
    var.set("复盘完成！")

def start_replay():
    var.set("复盘中，请稍候……（时间较久，请耐心等待）")
    refreshThread = threading.Thread(target = replay)    
    refreshThread.start()
    
def start_live():
    #try:
    config = Config("config.ini")
    #except:
    #    var.set("配置文件错误，请按指示设置")
    #    return
    fileLookUp = FileLookUp()
    fileLookUp.initFromConfig(config)
    var.set("准备完成！基准目录为：%s"%fileLookUp.basepath)
    liveListener = LiveListener(fileLookUp.basepath, config)
    liveListener.startListen()
    
    

b1 = tk.Button(window, text='复盘模式', bg='#ccffcc', width=12, height=1, command=start_replay)
b1.pack()
b1 = tk.Button(window, text='实时模式', bg='#ffcccc', width=12, height=1, command=start_live)
b1.pack()

l = tk.Label(window, textvariable=var, width=40, height=1)
l.pack()

window.mainloop()

