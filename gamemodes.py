from settings import Settings, GameSettings, HeadSwitchSettings, WithoutWallSettings, SubSettings


class Gamemode:
    """Fasst Spielklassen und Subsettingsklassen zusammens"""
    def __init__(self, gameclass, subsettingsclass : SubSettings = None):
        self.gameclass = gameclass
        self.subsettings = None

        self._subsettingsclass = subsettingsclass
        self._settings = None

        self.plane = None

    def init(self, settings: Settings, ui_manager):
        self._settings = settings
        if self._subsettingsclass is not None:
            self.subsettings = self._subsettingsclass(settings, ui_manager)
            self.plane = self.subsettings.setup()

    @property
    def screen(self):
        from pygame.display import set_mode
        return set_mode(self._settings.size)
    
    @property
    def has_subsettings(self) -> bool:
        return self.subsettings is not None

    def run_game(self, loggerfile, lvl) -> bool:
        game = self.gameclass(self._settings, loggerfile, lvl, {} if not self.has_subsettings else self.subsettings.get_config())
        game.run()
        return game.quit

    def save(self, logger=None):
        """Ruft die Save-Methode der Subsettings auf, falls vorhanden"""
        if self.has_subsettings:
            #print("save", self.subsettings, logger)
            self.subsettings.save(logger)

    def isquit(self, ui_element) -> bool:
        if not self.has_subsettings:
            return False
        return self.subsettings.isquit(ui_element)

    def set_subsettings_visibility(self, visible: bool):
        if not self.has_subsettings:
            return

        if visible:
            self.plane.show()
        else:
            self.plane.hide()


def get_gamemodes():
    from game import Game, WithoutWall, HeadSwitch
    from mods import mod_gamemodes
    HeadSwitch_Gamemode = Gamemode(HeadSwitch, HeadSwitchSettings)
    WithoutWall_Gamemode = Gamemode(WithoutWall, WithoutWallSettings)
    Game_Gamemode = Gamemode(Game, GameSettings)

    StandardGamemodes = {"Normal": Game_Gamemode, "Kopftausch": HeadSwitch_Gamemode,
            "Wandlos": WithoutWall_Gamemode}


    StandardGamemodes.update(mod_gamemodes())
    return StandardGamemodes
