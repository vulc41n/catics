import os
import yaml

class Config:
    def __init__(self):
        self.path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            'config.yml'
        )
        with open(self.path, 'r') as f:
            self.config = yaml.safe_load(f.read())

    def __getitem__(self, key: str):
        return self.config[key]

    def set(self, **kwargs):
        for k, v in kwargs.items():
            self.config[k] = v

    def save(self):
        with open(self.path, 'w') as f:
            f.write(yaml.dump(self.config))
