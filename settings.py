import json
import os
import sys
from typing import List, Tuple, Union

class Settings:
    def __init__(self, path="gameconfig.json", autosave: bool = False):
        self.path = path
        self.load()
        self.autosave = autosave

    def load(self) -> bool:
        with open(self.path, "r") as file:
            self.content = json.load(file)

        if not os.path.exists(f"textures/{self.content.get('texturepack')}"):
            print(f"Couldn't find {self.content.get('texturepack')}, replacing with 'default'", file=sys.stderr)
            self.content["texturepack"] = "default"
            self.save()

    def save(self) -> None:
        with open(self.path, "w") as file:
            json.dump(self.content, file)

    def copy(self, autosave: bool = False):
        return Settings(self.path, autosave)

    @property
    def gamemode(self):
        return self.content.get("gamemode")

    @gamemode.setter
    def gamemode(self, obj):
        self.content["gamemode"] = obj
        if self.autosave:
            self.save()

    @property
    def size(self) -> List[int]:
        return self.content.get("size")

    @property
    def realsize(self) -> Tuple[int, int]:
        return self.content.get("size")[0]*self.tilesize[0], self.content.get("size")[1]*self.tilesize[1]

    @size.setter
    def size(self, size: Union[Tuple[int, int], List[int]]):
        self.content["size"] = size
        if self.autosave:
            self.save()

    @property
    def snakespeed(self) -> int:
        return self.content.get("snakespeed")

    @snakespeed.setter
    def snakespeed(self, obj):
        self.content["snakespeed"] = obj
        if self.autosave:
            self.save()

    @property
    def fps(self) -> int:
        return self.content.get("fps")

    @fps.setter
    def fps(self, obj):
        self.content["fps"] = obj
        if self.autosave:
            self.save()

    @property
    def tilesize(self):
        return self.content.get("tilesize")

    @tilesize.setter
    def tilesize(self, obj):
        if isinstance(obj, (tuple, list)) and len(obj) == 2:
            self.content["tilesize"] = obj
            if self.autosave:
                self.save()

    @property
    def texturepack(self):
        return self.content.get("texturepack")

    @texturepack.setter
    def texturepack(self, name: str):
        self.content["texturepack"] = name
        if self.autosave:
            self.save()
