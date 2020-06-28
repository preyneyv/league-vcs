"""
This is the long-running main entry point for the whole application. It runs at startup and gets minimized to the
system tray.
"""
import datetime
import os
import sys

from league_vcs.config import Config
from league_vcs.gui import GUI
from league_vcs.gui.utils import Singleton

if getattr(sys, 'frozen', False):
    _file_ = sys.executable
else:
    _file_ = __file__

dir_ = os.path.dirname(os.path.realpath(_file_))
os.makedirs(os.path.join(dir_, 'logs'), exist_ok=True)


class DuplicateStream:
    def __init__(self, *streams):
        self.streams = [stream for stream in streams if stream is not None]

    def write(self, s: str) -> int:
        retval = None
        for stream in self.streams:
            retval = stream.write(s)
            stream.flush()

        return retval

    def flush(self) -> None:
        for stream in self.streams:
            stream.flush()


log_name = datetime.datetime.now().isoformat().replace(':', '-').replace('.', '-') + '.log'
log_file = open(os.path.join(dir_, 'logs', log_name), 'w')
sys.__stdout__ = sys.stdout = DuplicateStream(log_file, sys.stdout)
sys.__stderr__ = sys.stderr = DuplicateStream(log_file, sys.stderr)

config_path = os.path.join(dir_, 'user_settings.json')
config = Config(config_path)

print('Loaded config', config)

if __name__ == '__main__':
    if len(sys.argv) == 1:
        gui = GUI(config)
        singleton = Singleton()
        if singleton.should_close():
            # There's already another instance running.
            print('There is another already-running instance. Exiting now.')
            sys.exit(1)

        gui.start()
    else:
        gui = GUI(config)
        gui.watch(sys.argv[1])
