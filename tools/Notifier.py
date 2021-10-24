# Created by moeheart at 09/12/2021
# 维护win10toast的展示。

class Notifier():
    '''
    通知展示类。
    '''

    def show(self, title, content):
        '''
        展示一条消息。
        params:
        - title: 标题。
        - content: 内容。
        '''
        if self.mode == "toast":
            self.toaster.show_toast(title, content, icon_path='icons/jx3bla.ico')
        else:
            print(title, content)

    def __init__(self, mode="toast"):
        '''
        初始化.
        '''
        self.mode = mode
        if mode == "toast":
            from win10toast import ToastNotifier
            self.toaster = ToastNotifier()
        else:
            pass
