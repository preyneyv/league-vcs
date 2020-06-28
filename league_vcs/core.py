import os
import subprocess
from typing import Optional

import win32api
import win32con
import win32process
from large_vcs import LargeVCS

from league_vcs.exceptions import UserInputException
from league_vcs.parsers import ROFLParser, GameParser

repo: Optional[LargeVCS] = None


def set_repo_path(path):
    """
    Use a specific repo path instead of the default one.
    This should be called before any other core functions.
    """
    global repo
    repo = LargeVCS.load_or_create(path)


def can_update(game_path):
    """
    Check if we can update our repository from the given game path.
    """
    game = GameParser(game_path)
    version = game.version
    return version, version not in repo.list()


def add(directory):
    """
    Add a game version to the repository, if we don't already have it.
    This looks for a file named "League of Legends.exe" in that directory.
    """
    game_path = os.path.join(directory, GameParser.executable_name)
    version, is_new = can_update(game_path)
    if not is_new:
        raise ValueError(f'Already have patch {version}.')

    print(f'Adding patch {version} to repository.')
    print(f'This may take a while.')
    repo.add(directory, version)


def set_high_priority(pid):
    handle = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, True, pid)
    win32process.SetPriorityClass(handle, win32process.HIGH_PRIORITY_CLASS)


def watch(replay):
    """
    Load the required game version and launch the replay viewer.
    """
    rofl = ROFLParser(replay)
    game_version = rofl.version
    supported = repo.list()
    if game_version not in supported:
        raise UserInputException(f'No game client found for patch {game_version}.')

    print(f'Restoring patch {game_version}...')
    repo.restore(game_version)

    game_path = repo.current_path(GameParser.executable_name)
    game_dir = repo.current_path()

    print('Launching replay...')
    p = subprocess.Popen([game_path, replay], cwd=game_dir)
    set_high_priority(p.pid)
    p.wait()
