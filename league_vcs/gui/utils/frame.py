import os

import wx


class Frame(wx.Frame):
    ICON_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'icons', 'small-icon.png'))

    def __init__(self, parent, id=wx.ID_ANY, title="", pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=wx.DEFAULT_FRAME_STYLE, name='LeagueVCSFrame'):
        super(Frame, self).__init__(parent, id, title, pos, size, style, name)
        icon = wx.Icon(wx.Bitmap(self.ICON_PATH, type=wx.BITMAP_TYPE_PNG))
        self.SetIcon(icon)


class CallbackFrame(Frame):
    def __init__(self, parent, id=wx.ID_ANY, title="", pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=wx.DEFAULT_FRAME_STYLE, name='LeagueVCSFrame'):
        super(CallbackFrame, self).__init__(parent, id, title, pos, size, style, name)
        self.close_callback = lambda: None

    def on_close(self, cb):
        self.close_callback = cb

    def Destroy(self):
        self.close_callback()
        return super(CallbackFrame, self).Destroy()

    def Close(self, force=False):
        self.close_callback()
        return super(CallbackFrame, self).Close(force=force)
