import os
import sys
import threading
from typing import Optional

import win32api
import win32com.client
import win32con
import win32process
import wx

from .frames import WatchReplayFrame, InitialConfigFrame, SettingsFrame
from .icons import icon
from .tray_item import TrayItem
from .. import core
from ..config import Config


class GUI:
    # SCAN_INTERVAL = 10 * 60 * 1000  # 10 minutes in millis
    SCAN_INTERVAL = 1 * 60 * 60 * 1000  # 1 hour in millis

    def __init__(self, config: Config):
        self.config = config
        self.app = wx.App()
        self.auto_scan_interval: Optional[wx.CallLater] = None
        self.tray_icon: Optional[TrayItem] = None

        self.scan_lock = threading.Lock()
        self.replay_frame = None
        self.settings_frame = None

        pid = win32api.GetCurrentProcessId()
        self.process_handle = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, True, pid)

    def set_priority(self, priority):
        """Make sure we're a low-priority process, since we're basically running forever."""
        win32process.SetPriorityClass(self.process_handle, priority)

    def set_low_priority(self):
        self.set_priority(win32process.IDLE_PRIORITY_CLASS)

    def set_high_priority(self):
        self.set_priority(win32process.ABOVE_NORMAL_PRIORITY_CLASS)

    def start(self):
        if self.config['configured']:
            # We already have config!
            self.start_daemon()
        else:
            # We don't have config
            frame = InitialConfigFrame(self.config, on_complete=self.start_daemon, on_cancel=self.exit)
            frame.Show()
        self.app.MainLoop()

    def start_daemon(self):
        self.install_startup()
        self.set_low_priority()
        self.tray_icon = TrayItem([], on_left_click=0)
        # Start the auto change poller.
        self.auto_scan_loop()

    def install_startup(self):
        if not getattr(sys, 'frozen', False):
            return
        # We're in an exe. Let's install startup thing.
        shell = win32com.client.Dispatch('WScript.Shell')
        startup_path = shell.SpecialFolders('Startup')
        path = os.path.join(startup_path, 'League VCS.lnk')
        if os.path.exists(path):
            return  # it's already there.
        target = sys.executable
        wDir = os.path.dirname(target)
        icn = sys.executable

        shortcut = shell.CreateShortCut(path)
        shortcut.Targetpath = target
        shortcut.WorkingDirectory = wDir
        shortcut.IconLocation = icn
        shortcut.save()

    def update_tray_menu(self):
        scan_option = ('Scanning...', None) if self.scan_lock.locked() else ('Scan Now', self.scan_game_directories)
        tray_menu = (
            ('Watch Replay', self.open_replay_picker),
            scan_option,
            None,
            ('Settings', self.open_settings),
            ('Exit', self.exit)
        )
        self.tray_icon.menu_options = tray_menu

    def auto_scan_loop(self):
        print('Checking for updates in the game folders.')
        threading.Thread(target=self._scan_game_directories, daemon=True, args=(False,)).start()
        self.auto_scan_interval = wx.CallLater(self.SCAN_INTERVAL, self.auto_scan_loop)

    def exit(self, *_):
        """
        Cleanup and exit.
        :param _:
        """
        if self.tray_icon:
            self.tray_icon.RemoveIcon()
            self.tray_icon.Destroy()
        if self.auto_scan_interval:
            self.auto_scan_interval.Stop()
        self.app.Destroy()
        sys.exit()

    def open_replay_picker(self, *_):
        if self.replay_frame:
            # Can only have one file picker open.
            return
        self.set_high_priority()
        self.replay_frame = wx.FileDialog(None, "Which replay would you like to watch?",
                                          wildcard="Replay of LoL (*.rofl)|*.rofl", style=wx.FD_OPEN)
        if self.replay_frame.ShowModal() == wx.ID_CANCEL:
            print('Cancelled watching a replay.')
            self.replay_frame = None
            self.set_low_priority()
            return
        file = self.replay_frame.GetPath()
        self.replay_frame = None

        WatchReplayFrame(file, self.config['repository']).on_complete(self.set_low_priority)

    def open_settings(self, *_):
        if self.settings_frame:
            self.settings_frame.Show(True)
            self.settings_frame.Raise()
            self.settings_frame.RequestUserAttention()
            return

        self.set_high_priority()
        frame = self.settings_frame = SettingsFrame(self.config)
        frame.Show()
        frame.on_close(self.set_low_priority)
        # self.tray_icon.ShowBalloon(title=f'To be implemented.', text='Lol')

    def scan_game_directories(self, *_):
        threading.Thread(target=self._scan_game_directories, daemon=True, args=(True,)).start()

    def _scan_game_directories(self, user_initiated=False):
        if self.scan_lock.locked():
            if user_initiated:
                self.tray_icon.ShowBalloon(title=f'Already in the middle of a scan.',
                                           text=f'Try again in a bit.')
            return

        with self.scan_lock:
            self.update_tray_menu()

            core.set_repo_path(self.config['repository'])
            to_update = []
            new_versions = set()
            for game_path in self.config['game_paths']:
                version, is_new = core.can_update(game_path)
                if is_new and version not in new_versions:
                    to_update.append((game_path, version))
                    new_versions.add(version)
            print('New versions', new_versions)
            if new_versions:
                self.tray_icon.ShowBalloon(title=f"Found new patch{'' if len(new_versions) == 1 else 'es'}!",
                                           text=f"Storing {', '.join(new_versions)} in the background.")
            elif user_initiated:
                # We gotta tell them we didn't find anything lol.
                self.tray_icon.ShowBalloon(title=f'No new patches found.',
                                           text=f"Your repository is all up to date!")

            for game_path, version in to_update:
                core.add(os.path.dirname(game_path))
                self.tray_icon.ShowBalloon(title=f'Added patch {version}!',
                                           text=f'Patch {version} has successfully been added to the repository.')

        self.update_tray_menu()
