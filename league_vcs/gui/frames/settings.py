import os
import subprocess

import wx
import wx.html

from .text_console import TextConsoleFrame
from ..components import make_header_container, confirm, file_picker
from ..utils.frame import CallbackFrame
from ... import core
from ...exceptions import UserInputException
from ...parsers import GameParser


class StaticWrapText(wx.PyControl):
    def __init__(self, parent, id=wx.ID_ANY, label='', pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=wx.NO_BORDER,
                 validator=wx.DefaultValidator, name='StaticWrapText'):
        wx.PyControl.__init__(self, parent, id, pos, size, style, validator, name)
        self.statictext = wx.StaticText(self, wx.ID_ANY, label, style=style)
        self.wraplabel = label
        # self.wrap()

    def wrap(self):
        self.Freeze()
        self.statictext.SetLabel(self.wraplabel)
        self.statictext.Wrap(self.GetSize().width)
        self.Thaw()

    def DoGetBestSize(self):
        self.wrap()
        # print self.statictext.GetSize()
        self.SetSize(self.statictext.GetSize())
        return self.GetSize()


class Tab(wx.Panel):
    def __init__(self, notebook):
        super(Tab, self).__init__(notebook)
        self.SetBackgroundColour('#ffffff')


class AddPatchFrame(TextConsoleFrame):
    title = 'Adding Patch'

    def run(self, path, repository):
        core.set_repo_path(repository)
        core.add(os.path.dirname(path))
        print('All done!')


class DropPatchesFrame(TextConsoleFrame):
    title = 'Dropping Patches'

    def run(self, patches, repository):
        core.set_repo_path(repository)
        for patch in patches:
            print(f'Dropping {patch}...')
            core.repo.drop(patch)
        print('All done!')


class ExportPatchesFrame(TextConsoleFrame):
    title = 'Exporting Patches'

    def run(self, patches, repository, destination):
        core.set_repo_path(repository)
        for patch in patches:
            dest_path = os.path.join(destination, patch.replace('.', '-'))
            print(f'Exporting {patch} to {dest_path}...')
            if os.path.exists(dest_path):
                raise ValueError(f'Destination path {dest_path} already exists! Please delete it and try again.')
            os.makedirs(dest_path)
            core.repo.export(patch, dest_path)
        print('All done!')


class RestorePatchFrame(TextConsoleFrame):
    title = 'Restoring Patch'

    def run(self, patch, repository):
        core.set_repo_path(repository)
        if core.repo.current() == patch:
            print(f'Deselecting patch {patch}...')
            core.repo.clean()
        else:
            print(f'Restoring patch {patch}...')
            core.repo.restore(patch)
        print('All done!')


class PatchesTab(Tab):
    def __init__(self, notebook, config):
        self.config = config
        self.patches = []
        super(PatchesTab, self).__init__(notebook)

        container = wx.BoxSizer()
        vbox = wx.BoxSizer(wx.VERTICAL)
        container.Add(vbox, 1, wx.EXPAND | wx.ALL, 12)

        # Patch list
        self.list_ctrl = list_ctrl = wx.ListCtrl(
            self, size=(-1, 300),
            style=wx.LC_REPORT | wx.BORDER_SUNKEN
        )
        vbox.Add(list_ctrl, 1, wx.EXPAND)
        list_ctrl.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_selection_change)
        list_ctrl.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.on_selection_change)
        list_ctrl.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_restore)

        # BUTTONS
        button_container = wx.BoxSizer()
        vbox.Add(button_container, 0, wx.EXPAND | wx.TOP, 6)

        add_button = wx.Button(self, label='Add')
        button_container.Add(add_button, 1, wx.RIGHT, 3)
        add_button.SetToolTip('Perform a one-time addition of a game executable into the repository.')
        add_button.Bind(wx.EVT_BUTTON, self.on_add)

        self.drop_button = drop_button = wx.Button(self, label='Drop')
        button_container.Add(drop_button, 1, wx.RIGHT | wx.LEFT, 3)
        drop_button.SetToolTip('Delete the selected patch.')
        drop_button.Bind(wx.EVT_BUTTON, self.on_drop)

        self.export_button = export_button = wx.Button(self, label='Export')
        button_container.Add(export_button, 1, wx.LEFT, 3)
        export_button.SetToolTip('Export the selected patch.')
        export_button.Bind(wx.EVT_BUTTON, self.on_export)

        hint = wx.StaticText(self, label='These are the patches you have stored in your repository.')
        hint.SetFont(wx.SMALL_FONT)
        hint.SetForegroundColour('#888888')
        vbox.Add(hint, 0, wx.TOP, 12)

        self.populate_list()
        self.SetSizerAndFit(container)
        self.Bind(wx.EVT_SHOW, self.on_show_toggle, self)

    def on_show_toggle(self, _):
        if self.IsShown():
            self.populate_list()

    def populate_list(self):
        core.set_repo_path(self.config['repository'])
        # print(core.repo.list(), core.repxo.current())
        current = core.repo.current()
        patches = self.patches = list(sorted(core.repo.list(), reverse=True))
        self.list_ctrl.ClearAll()
        self.list_ctrl.InsertColumn(0, 'Patch Version', width=200)
        self.list_ctrl.InsertColumn(1, 'Active?', width=100)
        for i, patch in enumerate(patches):
            self.list_ctrl.InsertItem(i, patch)
            if patch == current:
                self.list_ctrl.SetItem(i, 1, 'Yes')
        self.on_selection_change(None)

    def on_selection_change(self, _):
        count = self.list_ctrl.GetSelectedItemCount()
        has_selected = count != 0
        self.export_button.Enable(has_selected)
        self.drop_button.Enable(has_selected)

    def get_selected(self):
        selection = []
        index = -1
        while len(selection) != self.list_ctrl.GetSelectedItemCount():
            index = self.list_ctrl.GetNextSelected(index)
            selection.append(index)
        return [self.patches[i] for i in selection]

    def on_restore(self, _):
        selected = self.get_selected()
        if len(selected) != 1:
            return

        RestorePatchFrame(selected[0], self.config['repository']).on_complete(self.populate_list)

    def on_add(self, _):
        path = file_picker('Which game executable would you like to add?',
                           'League of Legends.exe|League of Legends.exe')
        if not path:
            return
        try:
            game = GameParser(path)
        except UserInputException as e:
            wx.MessageBox(str(e), 'Error', style=wx.ICON_ERROR)
            return
        if game.version in self.patches:
            wx.MessageBox(f'We already have patch {game.version}!', "Can't Add", style=wx.ICON_INFORMATION)
            return
        AddPatchFrame(path, self.config['repository']).on_complete(self.populate_list)

    def on_drop(self, _):
        to_drop = self.get_selected()
        answer = confirm(self, f'Are you sure you want to drop {", ".join(to_drop)}?\n'
                               f'This can\'t be undone!',
                         f'Dropping {len(to_drop)} Patch{"" if len(to_drop) == 1 else "es"}',
                         style=wx.ICON_WARNING)
        if not answer:
            return
        DropPatchesFrame(to_drop, self.config['repository']).on_complete(self.populate_list)

    def on_export(self, _):
        to_export = self.get_selected()
        with wx.DirDialog(self, "Where do you want to export these patches?") as modal:
            if modal.ShowModal() == wx.ID_CANCEL:
                return
            else:
                path = modal.GetPath()
        ExportPatchesFrame(to_export, self.config['repository'], path)


class GamePathsTab(Tab):
    def __init__(self, notebook, config):
        self.config = config
        self.game_paths = []
        super(GamePathsTab, self).__init__(notebook)

        container = wx.BoxSizer()
        vbox = wx.BoxSizer(wx.VERTICAL)
        container.Add(vbox, 1, wx.EXPAND | wx.ALL, 12)

        # Patch list
        self.list_ctrl = list_ctrl = wx.ListCtrl(
            self, size=(-1, 300),
            style=wx.LC_REPORT | wx.BORDER_SUNKEN | wx.LC_SINGLE_SEL
        )
        vbox.Add(list_ctrl, 1, wx.EXPAND)
        list_ctrl.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_selection_change)
        list_ctrl.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.on_selection_change)
        list_ctrl.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_activate)

        # BUTTONS
        button_container = wx.BoxSizer()
        vbox.Add(button_container, 0, wx.EXPAND | wx.TOP, 6)

        add_button = wx.Button(self, label='Add')
        button_container.Add(add_button, 1, wx.RIGHT, 3)
        add_button.SetToolTip('Perform a one-time addition of a game executable into the repository.')
        add_button.Bind(wx.EVT_BUTTON, self.on_add)

        self.drop_button = drop_button = wx.Button(self, label='Drop')
        button_container.Add(drop_button, 1, wx.LEFT, 3)
        drop_button.SetToolTip('Delete the selected patch.')
        drop_button.Bind(wx.EVT_BUTTON, self.on_drop)

        hint = wx.StaticText(self, label='These are game paths that we watch for new patches in.')
        hint.SetFont(wx.SMALL_FONT)
        hint.SetForegroundColour('#888888')
        vbox.Add(hint, 0, wx.TOP, 12)

        self.populate_list()
        self.SetSizerAndFit(container)

    def populate_list(self):
        paths = self.game_paths = self.config['game_paths']
        self.list_ctrl.ClearAll()
        self.list_ctrl.InsertColumn(0, 'Path', width=200)
        self.list_ctrl.InsertColumn(1, 'Version', width=100)
        for i, path in enumerate(paths):
            self.list_ctrl.InsertItem(i, path)
            try:
                game = GameParser(path)
                self.list_ctrl.SetItem(i, 1, game.version)
            except UserInputException:
                self.list_ctrl.SetItem(i, 1, 'Error')

        self.on_selection_change(None)

    def on_selection_change(self, _):
        count = self.list_ctrl.GetSelectedItemCount()
        has_selected = count != 0
        self.drop_button.Enable(has_selected)

    def get_selected(self):
        idx = self.list_ctrl.GetFirstSelected()
        return self.game_paths[idx]

    def on_add(self, _):
        path = file_picker('Which game executable would you like to add?',
                           'League of Legends.exe|League of Legends.exe')
        if not path:
            return
        try:
            version = GameParser(path).version
        except UserInputException as e:
            wx.MessageBox(str(e), 'Error', style=wx.ICON_ERROR)
            return
        if path in self.game_paths:
            wx.MessageBox(f'We already have that game path!', "Can't Add", style=wx.ICON_INFORMATION)
            return

        self.config['game_paths'].append(path)
        self.config.save()
        self.populate_list()
        core.set_repo_path(self.config['repository'])

        if version not in core.repo.list():
            AddPatchFrame(path, self.config['repository']).on_complete(self.populate_list)

    def on_drop(self, _):
        selected = self.get_selected()
        self.config['game_paths'].remove(selected)
        self.config.save()
        self.populate_list()

    def on_activate(self, _):
        selected = self.get_selected()
        subprocess.Popen(f'explorer /select,{selected}')


class CustomHTMLWindow(wx.html.HtmlWindow):
    def OnLinkClicked(self, link):
        wx.LaunchDefaultBrowser(link.GetHref())


class AboutTab(Tab):
    def __init__(self, notebook):
        super(AboutTab, self).__init__(notebook)
        sizer = wx.BoxSizer(wx.VERTICAL)
        window = CustomHTMLWindow(self, style=wx.html.HW_NO_SELECTION)
        text = """
        <p>This application helps preserve your old League of Legends versions semi-automatically,
           primarily for the purposes of watching old replays.</p>
        <p>It achieves this by storing only the changes from each patch, as opposed to every single file.
           In practice, this ends up saving a lot of storage space while still allowing you to rapidly jump
           back in time to any previous version.</p>
        <p>If you are interested in more details, you can check out the source code on
           <a href='https://www.youtube.com/watch?v=dQw4w9WgXcQ'>GitHub</a> to figure out how exactly I'm doing
           this.</p>
        <p>Long story short, this project is a consequence of the global health crisis.</p>"""
        window.SetPage(text)
        sizer.Add(window, 1, wx.EXPAND)
        self.SetSizer(sizer)


class SettingsFrame(CallbackFrame):
    def __init__(self, config):
        super(SettingsFrame, self).__init__(None, title='League VCS',
                                            style=wx.DEFAULT_FRAME_STYLE)  # & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
        self.config = config
        self.SetBackgroundColour('#ffffff')
        # self.SetBackgroundColour('#f0f0f0')

        container = wx.BoxSizer()
        vbox = wx.BoxSizer(wx.VERTICAL)
        container.Add(vbox, 1, wx.EXPAND | wx.ALL, 12)

        # Add the title
        header_container = make_header_container(self)
        vbox.Add(header_container, 0, wx.BOTTOM, border=12)

        # Add the tabs.
        nb = wx.Notebook(self)

        patches_tab = PatchesTab(nb, config)
        game_paths_tab = GamePathsTab(nb, config)
        about_tab = AboutTab(nb)

        nb.AddPage(patches_tab, 'Patches')
        nb.AddPage(game_paths_tab, 'Game Paths')
        nb.AddPage(about_tab, 'About')

        vbox.Add(nb, 1, wx.EXPAND | wx.ALL, 4)

        self.SetSizerAndFit(container)
