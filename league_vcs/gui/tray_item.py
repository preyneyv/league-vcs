import os

import wx
import wx.adv


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

        return menu

    def set_icon(self):
        icon = wx.Icon(wx.Bitmap(self.ICON_PATH, type=wx.BITMAP_TYPE_PNG))
        self.SetIcon(icon, self.TOOLTIP)

    def on_left_down(self, _):
        """Tray icon was left-clicked, trigger the required action."""
        if self.on_left_click is False:
            return
        self.menu_options[self.on_left_click][1]()
