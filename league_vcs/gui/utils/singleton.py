from win32api import CloseHandle, GetLastError
from win32event import CreateMutex
from winerror import ERROR_ALREADY_EXISTS


class Singleton:
    """ Limits application to single instance """

    def __init__(self):
        self.mutexname = "league_vcs_{13560846-8FB1-430F-B24B-2AE8A2F3CC71}"
        self.mutex = CreateMutex(None, False, self.mutexname)
        self.lasterror = GetLastError()

    def should_close(self):
        return self.lasterror == ERROR_ALREADY_EXISTS

    def __del__(self):
        if self.mutex:
            CloseHandle(self.mutex)
