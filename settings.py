import json
import os
import sys
from typing import List, Tuple, Union

import pygame_gui
import pygame

class Settings:
    def __init__(self, path="gameconfig.json", autosave: bool = False):
        self.path = path
        self.load()
        self.autosave = autosave

    def load(self) -> bool:
        from gamemodes import get_gamemodes
        with open(self.path, "r") as file:
            self.content = json.load(file)

        if not os.path.exists(f"textures/{self.content.get('texturepack')}"):
            print(f"Couldn't find {self.content.get('texturepack')}, replacing with 'default'", file=sys.stderr)
            self.content["texturepack"] = "default"
            self.save()

        if not self.content.get("gamemode") in get_gamemodes().keys():
            print(f"Couldn't find {self.content.get('texturepack')}, replacing with 'default'", file=sys.stderr)
            self.content["gamemode"] = "Normal"
            self.save()

    def save(self) -> None:
        with open(self.path, "w") as file:
            json.dump(self.content, file, indent=4)

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

    @property
    def gamemode_settings(self):
        return self.content.get("gamemode_settings")

class SubSettings:
    """Menüführung für Spielmodi"""
    def __init__(self, settings: Settings, ui_manager):
        self.settings = settings

        self.ui_elements = {}
        self.ui_manager = ui_manager

    def setup(self):
        from main import MAINSCREEN_SIZE
        plane = pygame_gui.elements.ui_panel.UIPanel(pygame.Rect(0, 0, *MAINSCREEN_SIZE), 1, self.ui_manager,
                                                              visible=0)
        self.ui_elements["plane"] = plane
        return plane

    def save(self, logger=None):
        """Speichert informationen"""
        raise NotImplementedError

    def isquit(self, ui_element):
        """Überprüft, ob der quit Knopf gedürckt wurde"""
        raise NotImplementedError

    def get_config(self):
        """Gibt zusätzliche Information bezüglich des Spielmodus"""
        return {}

class GameSettings(SubSettings):
    gamemode = "Normal"
    def setup(self):
        from main import center_objects
        plane = super().setup()
        snakespeedincrease_label_rect = pygame.Rect(-1, -1, 296, 20)
        snakespeedincrease_input_rect = pygame.Rect(-1, -1, 150, 50)
        snakespeedincrease_label_rect, snakespeedincrease_input_rect = center_objects(snakespeedincrease_label_rect, snakespeedincrease_input_rect,
                                                                      center_y=50)
        snakespeedincrease_label = pygame_gui.elements.UILabel(snakespeedincrease_label_rect, "Geschwindigkeitsanstieg der Schlange:",
                                                       self.ui_manager, plane)
        snakespeedincrease_input = pygame_gui.elements.UITextEntryLine(snakespeedincrease_input_rect, self.ui_manager, plane)
        snakespeedincrease_input.set_text(str(self.snakespeedincrease) + " ")
        self.ui_elements["snakespeedincrease_label"] = snakespeedincrease_label
        self.ui_elements["snakespeedincrease_input"] = snakespeedincrease_input

        # Komma dient dem 'tuple unpacking'
        back_button_rect, = center_objects(pygame.Rect(-1, -1, 150, 50), center_y=150)

        back_button = pygame_gui.elements.UIButton(
            relative_rect=back_button_rect,
            text="Zurück",
            manager=self.ui_manager,
            container=plane)
        self.ui_elements["back_button"] = back_button
        return plane

    def save(self, logger = None):
        speedincr = self.ui_elements["snakespeedincrease_input"].get_text()
        try:
            speedincr = float(speedincr)
            self.snakespeedincrease = speedincr
            if logger is not None:
                logger.debug(f"snakespeedincrease is set to {speedincr}")
        except ValueError:
            if logger is not None:
                logger.warning("given snakespeedincrease isn't a number ")
            self.ui_elements["snakespeedincrease_input"].set_text(str(self.snakespeedincrease))

    def isquit(self, ui_element):
        return ui_element == self.ui_elements.get("back_button")

    def get_config(self) -> dict:
        return {"speed_increase": self.snakespeedincrease}

    @property
    def snakespeedincrease(self):
        return self.settings.gamemode_settings.get(self.gamemode).get("speed_increase")

    @snakespeedincrease.setter
    def snakespeedincrease(self, obj):
        self.settings.gamemode_settings.get(self.gamemode)["speed_increase"] = obj
        if self.settings.autosave:
            self.settings.save()

class HeadSwitchSettings(GameSettings):
    gamemode="Kopfwechsel"

class WithoutWallSettings(GameSettings):
    gamemode = "Wandlos"
