import os

import wx
import wx.adv


#
# class TrayIcon(wx.adv.TaskBarIcon):
#     def __init__(self):
#         super(TrayIcon, self).__init__()
#         icon = wx.Icon(wx.Bitmap(r"C:/Users/prana/Downloads/black-small-square-geometric-37940.bmp"))
#         self.SetIcon(icon, 'wow Cooltip')
#

def create_menu_item(menu, label, func=None):
    item = wx.MenuItem(menu, -1, label)
    if func is None:
        item.Enable(False)
    else:
        menu.Bind(wx.EVT_MENU, func, id=item.GetId())
    menu.Append(item)
    return item


class TrayItem(wx.adv.TaskBarIcon):
    ICON_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'icons', 'small-icon.png'))
    TOOLTIP = 'League VCS'

    def __init__(self, menu_options, on_left_click=False):
        wx.adv.TaskBarIcon.__init__(self)
        self.set_icon()

        self.menu_options = menu_options
        self.on_left_click = on_left_click
        # self.on_exit_callback = on_exit_callback

        self.Bind(wx.adv.EVT_TASKBAR_LEFT_DOWN, self.on_left_down)

    def CreatePopupMenu(self):
        menu = wx.Menu()

        create_menu_item(menu, self.TOOLTIP, None)
        menu.AppendSeparator()

        for item in self.menu_options:
            if item is None:
                menu.AppendSeparator()
            else:
                label, func = item
                create_menu_item(menu, label, func)

        # menu.AppendSeparator()
        # create_menu_item(menu, 'Exit', self.on_exit)

        return menu

    def set_icon(self):
        icon = wx.Icon(wx.Bitmap(self.ICON_PATH, type=wx.BITMAP_TYPE_PNG))
        self.SetIcon(icon, self.TOOLTIP)

    def on_left_down(self, _):
        """Tray icon was left-clicked, trigger the required action."""
        if self.on_left_click is False:
            return
        self.menu_options[self.on_left_click][1]()

    # def on_hello(self, event):
    #     print('Hello, world!')

    # def on_exit(self, event):
    #     if self.on_exit_callback:
    #         self.on_exit_callback()
        # self.myapp_frame.Close()
