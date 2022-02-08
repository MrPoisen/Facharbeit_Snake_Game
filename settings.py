import json
from typing import List, Tuple, Union

class Settings:
    def __init__(self, path="gameconfig.json", tilesize: tuple = (20, 20), autosave: bool = False):
        self.path = path
        self.load()
        self.tilesize = tilesize
        self.autosave = autosave

    def load(self) -> bool:
        with open(self.path, "r") as file:
            self.content = json.load(file)

        return self._check()

    def save(self) -> None:
        with open(self.path, "w") as file:
            json.dump(self.content, file)

    def _check(self) -> bool:
        for elem in ("gamemode", "size", "snakespeed"):
            if elem not in self.content.keys():
                return False
        return True

    @property
    def gamemode(self):
        return self.content.get("gamemode")

    @gamemode.setter
    def gamemode(self, obj):
        self.content["gamemode"] = obj
        if self.autosave:
            self.save()

    @property
    def size(self) -> Tuple[int, int]:
        return tuple(self.content.get("size"))

    @size.setter
    def size(self, size: Union[Tuple[int, int], List[int]]):
        if size[0] % self.tilesize[0] != 0 or size[1] % self.tilesize[1]:  # if width or height doesn't fit the Tilesize
            # raise Exception("HEY, WRONG SIZE")
            print("WRONG SIZE")
            return
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
