from .text_console import TextConsoleFrame
from ... import core
from ...exceptions import UserInputException


class WatchReplayFrame(TextConsoleFrame):
    title = 'Watch Replay'

    def run(self, path, repository):
        core.set_repo_path(repository)
        print(f'Loading {path}')
        try:
            core.watch(path)
            print('All done!')
        except UserInputException as e:
            print(str(e))
