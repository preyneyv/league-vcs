import os
import sys

import wx

from league_vcs import core

if len(sys.argv) == 1:
    wx.App()
    with wx.FileDialog(None, "Watch a replay", wildcard="Replay of LoL (*.rofl)|*.rofl", style=wx.FD_OPEN) as modal:
        if modal.ShowModal() == wx.ID_CANCEL:
            print('Okay, never mind.')
            sys.exit()
        file = modal.GetPath()
    # o = win32ui.CreateFileDialog(1, None, None, 0, "Replay of LoL (*.rofl)|*.rofl|")
    # o.DoModal()
    # file = o.GetPathName()
    # if not file:
    #     print('Okay, nevermind.')
    #     sys.exit()
else:
    file = os.path.abspath(sys.argv[1])

try:
    core.watch(file)
except ValueError as e:
    print(str(e), file=sys.stderr)
    input('Press enter to exit...')
    sys.exit(1)
except FileNotFoundError as e:
    print(f"Couldn't find a replay at {file}", file=sys.stderr)
    input('Press enter to exit...')
    sys.exit(1)
