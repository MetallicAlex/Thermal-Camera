import os
import json


class Setting:
    def __init__(self, filename: str):
        self.app_path = os.path.dirname(os.getcwd())
        print(self.app_path)
        with open(filename) as file:
            data = json.load(file, strict=False)
            self.paths = data['paths']
        with open(f'{self.app_path}/{self.paths["lang"]}/{data["lang"]}.json', encoding='utf8') as file:
            self._lang = json.load(file, strict=False)
        with open(f'{self.app_path}/{self.paths["themes"]}/{data["theme"]}.json') as file:
            self._theme = json.load(file, strict=False)

    @property
    def lang(self):
        return self._lang

    @property
    def theme(self):
        return self._theme