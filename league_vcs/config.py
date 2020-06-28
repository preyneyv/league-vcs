import json


class Config(dict):
    """
    A custom config class with default values.
    """
    defaults = {
        'game_paths': [],
        'repository': None,
        'configured': False
    }

    def __init__(self, path):
        self._path = path
        try:
            with open(path) as config_file:
                config = json.load(config_file)
        except FileNotFoundError:
            config = {}

        super(Config, self).__init__({
            **self.defaults,
            **config
        })
        self.save()

    def save(self):
        with open(self._path, 'w') as config_file:
            json.dump(self, config_file)
        print('Wrote config', self)
