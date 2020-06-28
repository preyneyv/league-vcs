import os

from win32api import GetFileVersionInfo

from league_vcs.exceptions import UserInputException


class GameParser:
    """
    Parse a League of Legends.exe game file.
    """

    executable_name = 'League of Legends.exe'

    def __init__(self, path):
        self.path = path
        assert os.path.exists(path), f'No file found at {path}!'
        try:
            self.version = self.extract_version()
        except BaseException:
            raise UserInputException(f'Invalid game executable at {path}!')

    def extract_version(self):
        langs = GetFileVersionInfo(self.path, r'\VarFileInfo\Translation')
        key = r'StringFileInfo\%04x%04x\FileVersion' % (langs[0][0], langs[0][1])
        return GetFileVersionInfo(self.path, key)
