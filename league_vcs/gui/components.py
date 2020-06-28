import wx

from .icons import icon


def make_header_container(parent):
    """Make a title element (with a logo and the name of this application)"""
    header_container = wx.BoxSizer()

    logo_img = wx.Image(icon('icon.png'), wx.BITMAP_TYPE_PNG).Scale(64, 64)
    logo = wx.StaticBitmap(parent, bitmap=logo_img.ConvertToBitmap())
    header_container.Add(logo, 0, wx.RIGHT, border=20)

    title = wx.BoxSizer(wx.VERTICAL)
    title_1 = wx.StaticText(parent, label='Unofficial*')
    title_1.SetForegroundColour('#aaaaaa')
    title_1.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.LIGHT))
    title.Add(title_1, 0)

    title_2 = wx.StaticText(parent, label='League VCS')
    title_2.SetFont(wx.Font(24, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.BOLD))
    title.Add(title_2, 0)
    header_container.Add(title, 1, wx.CENTER)

    return header_container


def confirm(parent, message, caption, style=0):
    dlg = wx.MessageDialog(parent, message, caption, style=wx.YES_NO | wx.NO_DEFAULT | style)
    return dlg.ShowModal() == wx.ID_YES


def file_picker(title, wildcard):
    modal = wx.FileDialog(None, title, wildcard=wildcard, style=wx.FD_OPEN)
    if modal.ShowModal() == wx.ID_CANCEL:
        return None
    return modal.GetPath()


def directory_picker(title):
    modal = wx.DirDialog(None, title)
    if modal.ShowModal() == wx.ID_CANCEL:
        return None
    return modal.GetPath()
