import wx

from ..components import make_header_container, file_picker, directory_picker
from ..utils import Frame


class InitialConfigFrame(Frame):
    game_path_example = 'E.g. C:\\Riot Games\\League of Legends\\Game\\League of Legends.exe'
    repository_path_example = 'E.g. D:\\Big Things\\League Repo\\'

    def __init__(self, config, on_complete, on_cancel):
        super(InitialConfigFrame, self).__init__(parent=None, title='Initial Configuration',
                                                 style=wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
        self.config = config
        self.on_complete = on_complete
        self.on_cancel = on_cancel
        self.game_path = None
        self.repository_path = None

        self.SetBackgroundColour('#ffffff')

        container = wx.BoxSizer()
        vbox = wx.BoxSizer(wx.VERTICAL)
        container.Add(vbox, 0, wx.EXPAND | wx.ALL, border=20)

        # Title
        header_container = make_header_container(self)
        vbox.Add(header_container, 0, wx.BOTTOM, border=20)

        # Small Introduction
        subtext = wx.StaticText(self, label="Welcome to the (unofficial) League of Legends Version Control System!\n"
                                            "There's just a bit of one-time information we need from you.")
        vbox.Add(subtext, 0, wx.BOTTOM, 20)

        # Game Path
        game_path_label = wx.StaticText(self, label='Where is your game installation?')
        game_path_label.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.BOLD))
        vbox.Add(game_path_label)

        game_path_container = wx.BoxSizer()
        vbox.Add(game_path_container)
        game_path_value = self.game_path_value = wx.StaticText(self,
                                                               label=self.game_path_example,
                                                               size=(300, 16), style=wx.ST_ELLIPSIZE_MIDDLE)
        game_path_container.Add(game_path_value, 0, wx.CENTER | wx.RIGHT, 10)

        game_path_picker = wx.Button(self, label='Select')
        game_path_container.Add(game_path_picker, 0, wx.CENTER)

        game_path_picker.Bind(wx.EVT_BUTTON, self.pick_game_path)

        # Repository Path
        repository_path_label = wx.StaticText(self, label='Where do you want to keep old game versions?')
        repository_path_label.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.BOLD))
        vbox.Add(repository_path_label, 0, wx.TOP, 20)

        repository_path_sub = wx.StaticText(self, label='This can get really large really quickly (think tens of GB), '
                                                        'so you should keep this on a large drive.')
        repository_path_sub.Wrap(subtext.GetSize().width)
        repository_path_sub.SetForegroundColour('#aaaaaa')
        vbox.Add(repository_path_sub)

        repository_path_container = wx.BoxSizer()
        vbox.Add(repository_path_container)

        repository_path_value = self.repository_path_value = wx.StaticText(self,
                                                                           label=self.repository_path_example,
                                                                           size=(300, 16), style=wx.ST_ELLIPSIZE_MIDDLE)
        repository_path_container.Add(repository_path_value, 0, wx.CENTER | wx.RIGHT, 10)

        repository_path_picker = wx.Button(self, label='Select')
        repository_path_container.Add(repository_path_picker, 0, wx.CENTER)

        repository_path_picker.Bind(wx.EVT_BUTTON, self.pick_repository_path)

        # Finalization actions
        self.save_button = save_button = wx.Button(self, label='Save Configuration')
        vbox.Add(save_button, 0, wx.EXPAND | wx.TOP, 20)
        save_button.Enable(False)
        save_button.Bind(wx.EVT_BUTTON, self.save_and_return)

        self.SetSizerAndFit(container)
        self.SetSizerAndFit(container)
        self.bind_events()

    def bind_events(self):
        self.Bind(wx.EVT_CLOSE, self.close_window)

    def close_window(self, evt: wx.Event):
        evt.StopPropagation()
        print('Exiting without complete configuration.')
        self.Destroy()
        self.on_cancel()

    def save_and_return(self, _):
        self.config['game_paths'] = [self.game_path]
        self.config['repository'] = self.repository_path
        self.config['configured'] = True
        self.config.save()
        print('Successfully saved configuration.')
        self.Destroy()
        self.on_complete()

    def pick_game_path(self, _):
        path = file_picker('Where is your game installation?',
                           'League of Legends.exe|League of Legends.exe')
        if path:
            self.game_path = path
            self.config['game_paths'] = [path]
            self.game_path_value.SetLabelText(path)
            self.game_path_value.SetSize(300, 16)
        else:
            self.game_path = None
            self.game_path_value.SetLabelText(self.game_path_example)
            self.game_path_value.SetSize(300, 16)

        self.check_enable_save()

    def pick_repository_path(self, _):
        path = directory_picker("Where do you want to keep old game versions?")
        if path:
            self.repository_path = path
            self.repository_path_value.SetLabelText(path)
            self.repository_path_value.SetSize(300, 16)
        else:
            self.repository_path = None
            self.repository_path_value.SetLabelText(self.repository_path_example)
            self.repository_path_value.SetSize(300, 16)

        self.check_enable_save()

    def check_enable_save(self):
        can_continue = self.game_path is not None and self.repository_path is not None
        self.save_button.Enable(can_continue)
