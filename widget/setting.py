import os
import json


class Setting:
    def __init__(self, filename: str):
        self.app_path = os.path.dirname(os.getcwd())
        print(self.app_path)
        self._filename = filename
        with open(filename) as file:
            data = json.load(file, strict=False)
            self._data = data
            self.paths = data['paths']
        with open(f'{self.app_path}/{self.paths["lang"]}/{data["lang"]}.json', encoding='utf8') as file:
            if data["lang"] == 'ru':
                self._lang = json.load(file, strict=False)
            else:
                self._lang = json.load(file)
        with open(f'{self.app_path}/{self.paths["themes"]}/{data["theme"]}.json') as file:
            self._theme = json.load(file, strict=False)

    @property
    def lang(self):
        return self._lang

    @property
    def theme(self):
        return self._theme

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        self._data = value

    def save(self):
        with open(f'{self.app_path}/{self.paths["lang"]}/{self.data["lang"]}.json', encoding='utf8') as file:
            if self.data["lang"] == 'ru':
                self._lang = json.load(file, strict=False)
            else:
                self._lang = json.load(file)
        with open(self._filename, 'w', encoding='utf-8') as file:
            json.dump(self.data, file, ensure_ascii=False, indent=4)