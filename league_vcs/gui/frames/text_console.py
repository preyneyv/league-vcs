import contextlib
import sys
import threading
import traceback

import wx

from ..icons import icon
from ..utils import Frame


class CallbackStringIO:
    def __init__(self, callback):
        self.callback = callback

    def write(self, s: str):
        sys.__stdout__.write(s)
        self.callback(s)

    def flush(self):
        pass


class TextConsoleFrame(Frame):
    title = 'Text Console'

    def __init__(self, *args, **kwargs):
        self.is_done = False
        self.complete_callback = lambda: ...
        super(TextConsoleFrame, self).__init__(parent=None,
                                               title=self.title,
                                               # style=wx.NO_BORDER)
                                               style=wx.CAPTION)
        self.SetBackgroundColour('#ffffff')

        container = wx.BoxSizer()
        hbox = wx.BoxSizer()
        container.Add(hbox, 0, wx.ALL, 20)

        logo_img = wx.Image(icon('icon.png'), wx.BITMAP_TYPE_PNG).Scale(64, 64)
        logo = wx.StaticBitmap(self, bitmap=logo_img.ConvertToBitmap())
        hbox.Add(logo, 0, wx.ALIGN_TOP | wx.RIGHT, border=20)

        self.text_box = text_box = wx.BoxSizer(wx.VERTICAL)
        hbox.Add(text_box)

        title = wx.StaticText(self, label=self.title)
        title.SetFont(wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.BOLD))
        text_box.Add(title, 0, wx.BOTTOM, 8)

        text = self.text = wx.TextCtrl(self, value='', size=(800, 250),
                                       style=wx.TE_MULTILINE | wx.SUNKEN_BORDER | wx.TE_READONLY | wx.TE_DONTWRAP)
        text.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.NORMAL))
        text_box.Add(text, 0, wx.BOTTOM, 16)

        self.close_btn = wx.Button(self, label='Close')
        self.close_btn.Show(False)
        self.text_box.Add(self.close_btn, 0, wx.ALIGN_RIGHT)
        self.close_btn.Bind(wx.EVT_BUTTON, lambda *_: self.Destroy())

        self.SetSizerAndFit(container)

        self.Bind(wx.EVT_CLOSE, self.on_close)

        self.Show()
        threading.Thread(target=self.capture, args=args, kwargs=kwargs).start()

    def _update(self, text):
        self.text.AppendText(text)

    def update(self, text):
        wx.CallAfter(self._update, text)

    def on_close(self, _):
        if self.is_done:
            self.Destroy()
        return self.is_done

    def on_complete(self, cb):
        if self.is_done:
            cb()
        else:
            self.complete_callback = cb

    def run(self, *args, **kwargs):
        pass

    def done(self):
        self.close_btn.Show(True)
        self.complete_callback()
        self.is_done = True
        self.Fit()

    def capture(self, *args, **kwargs):
        output = CallbackStringIO(self.update)
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            try:
                self.run(*args, **kwargs)
            except BaseException:
                print('An unexpected error occurred! More details follow:')
                print(traceback.format_exc())
        self.done()
