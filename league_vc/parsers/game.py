from win32api import GetFileVersionInfo


class GameParser:
    """
    Parse a League of Legends.exe game file.
    """

    def __init__(self, path):
        self.path = path
        self.version = self.extract_version()

    def extract_version(self):
        langs = GetFileVersionInfo(self.path, r'\VarFileInfo\Translation')
        key = r'StringFileInfo\%04x%04x\FileVersion' % (langs[0][0], langs[0][1])
        return GetFileVersionInfo(self.path, key)
