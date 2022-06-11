# Standardbibliothek
from typing import Tuple, Union
import logging
from datetime import datetime
from sys import argv
import os

# externe Bibliotheken
import pygame
import pygame_gui

# lokale Module
import game
from settings import Settings
from sprites import TexturePack
from gamemodes import get_gamemodes

# KONSTANTEN
MAINSCREEN_SIZE = (800, 600) # Größe des Hauptbildschirms
#TILE_SIZE = [30, 30] # Größe der Spielfelder

class MainMenu:
    def __init__(self, settings: Settings = None, logging_=False, lvl=logging.DEBUG):
        # Einstellungen
        if settings is None:
            settings = Settings(autosave=True)
        self.available_gamemodes = get_gamemodes()
        self.settings = settings

        # logging
        self.logger = None
        self.logger_file = None # Dateiname der Log-Datei
        self.logging = logging_
        self.logging_lvl = lvl
        if logging_:
            self.logger = logging.getLogger(__name__)
            self.logger.setLevel(lvl)
            if not os.path.exists("logs"): # Erstellt den logs Ordner, falls es ihn noch nicht gibt
                os.makedirs("logs")
            self.logger_file = f"logs/{datetime.now().strftime('%d-%m-%Y %H.%M.%S')}.log"
            format = logging.Formatter('%(name)s -> %(asctime)s : %(levelname)s : %(message)s', datefmt='%d/%m/%Y %H:%M:%S')
            fh = logging.FileHandler(self.logger_file) # Damit der logger in eine Datei schreibt
            fh.setLevel(lvl)
            fh.setFormatter(format)
            self.logger.addHandler(fh)
            self.logger.info(f"loaded settings: {self.settings.content}")

        # Pygame initialisieren
        pygame.init()
        # Titel
        pygame.display.set_caption("Snake")

        self.clock = pygame.time.Clock()
        self.screen = resize(MAINSCREEN_SIZE)

        # Benutzeroberfläche erstellen
        self.setup_ui()

        # Spielmodi vorbereiten
        self._init_gamemodes()

        self.running = False

    def get_curgamemode(self):
        return self.available_gamemodes.get(self.settings.gamemode)

    def _init_gamemodes(self):
        for name, game in self.available_gamemodes.items():
            game.init(self.settings, self.ui_manager)
            if name == self.settings.gamemode:
                if not game.has_subsettings:
                    self.ui_elements["gamemode_subsettings_button"].disable()


    def setup_main_plane(self):
        # main plane
        main_plane = pygame_gui.elements.ui_panel.UIPanel(pygame.Rect(0, 0, *MAINSCREEN_SIZE), 0, self.ui_manager, visible=0)
        self.ui_elements["main_plane"] = main_plane

        # Knopf der zu den Einstellungen führt
        settings = pygame_gui.elements.UIButton(
            relative_rect=center_object(pygame.Rect(200, 300, 200, 50), center_y=False),
            text="Einstellungen",
            manager=self.ui_manager,
            container=main_plane,
            visible=0)
        self.ui_elements["settings"] = settings

        # Knopf der das Spiel startet
        start = pygame_gui.elements.UIButton(
            relative_rect=center_object(pygame.Rect(200, 150, 200, 50), center_y=False),
            text="Start",
            manager=self.ui_manager,
            container=main_plane,
            visible=0)
        self.ui_elements["start"] = start

        # Text der sich über dem Startknopf befindet
        snake_title_text = pygame_gui.elements.UITextBox("<b>Snake Game<b>",
                                                         center_object(pygame.Rect(220, 100, 100, -1),
                                                                                     center_y=False, offset_x=50),
                                                         manager=self.ui_manager,
                                                         container=main_plane,
                                                         visible=0,
                                                         wrap_to_height=True
                                                         )
        self.ui_elements["snake_title_text"] = snake_title_text

        # Knopf um das Programm zu verlassen
        main_close_button = pygame_gui.elements.UIButton(
            relative_rect=center_object(pygame.Rect(200, 450, 200, 50), center_y=False),
            text="Schließen",
            manager=self.ui_manager,
            container=main_plane,
            visible=0)
        self.ui_elements["main_close_button"] = main_close_button

    def setup_settings_plane(self):
        # settings plane
        settings_plane = pygame_gui.elements.ui_panel.UIPanel(pygame.Rect(0, 0, *MAINSCREEN_SIZE), 0, self.ui_manager,
                                                              visible=0)
        self.ui_elements["settings_plane"] = settings_plane

        # Schlangengeschwindigkeit
        snakespeed_label_rect = pygame.Rect(-1, -1, 232, 21)
        snakespeed_input_rect = pygame.Rect(-1, -1, 150, 50)
        snakespeed_label_rect, snakespeed_input_rect = center_objects(snakespeed_label_rect, snakespeed_input_rect,
                                                                      center_y=50)
        snakespeed_label = pygame_gui.elements.UILabel(snakespeed_label_rect, "Geschwindigkeit der Schlange:",
                                                       self.ui_manager, settings_plane)
        snakespeed_input = pygame_gui.elements.UITextEntryLine(snakespeed_input_rect, self.ui_manager, settings_plane)
        snakespeed_input.set_text(str(self.settings.snakespeed))
        self.ui_elements["snakespeed_input"] = snakespeed_input
        self.ui_elements["snakespeed_label"] = snakespeed_label


        # Spielmodus
        gamemode_current_rect = pygame.Rect(200, 100, 200, 50)
        gamemode_selection_rect = pygame.Rect(200, 100, 150, 66)
        gamemode_current_rect, gamemode_selection_rect = center_objects(gamemode_current_rect, gamemode_selection_rect, center_y=150)
        gamemode_selection = pygame_gui.elements.ui_selection_list.UISelectionList(gamemode_selection_rect,
                                                                                  list(self.available_gamemodes.keys()),
                                                                                  self.ui_manager,
                                                                                  container=settings_plane)
        gamemode_current = pygame_gui.elements.UILabel(gamemode_current_rect,
                                                       f"Spielmodus: {self.settings.gamemode}",
                                                       self.ui_manager, settings_plane)

        self.ui_elements["gamemode_selection"] = gamemode_selection
        self.ui_elements["gamemode_current"] = gamemode_current

        # Spielmoduseinstellungen
        gamemode_subsettings_rect = gamemode_current_rect.move(0, 100).inflate(110, 1)
        gamemode_subsettings_button = pygame_gui.elements.UIButton(
            relative_rect=gamemode_subsettings_rect,
            text="Spielmodusspezifische Einstellungen",
            manager=self.ui_manager,
            container=settings_plane,
            visible=True)

        self.ui_elements["gamemode_subsettings_button"] = gamemode_subsettings_button

        # Texturen
        texture_current_rect = pygame.Rect(200, 100, 200, 50)
        texture_selection_rect = pygame.Rect(200, 100, 150, 66)
        texture_current_rect, texture_selection_rect = center_objects(texture_current_rect, texture_selection_rect, center_y=350)
        texture_selection = pygame_gui.elements.ui_selection_list.UISelectionList(texture_selection_rect,
                                                                                  TexturePack.texturpacks(),
                                                                                  self.ui_manager,
                                                                                  container=settings_plane)
        texture_current = pygame_gui.elements.UILabel(texture_current_rect,
                                                       f"Texturen: {self.settings.texturepack}",
                                                       self.ui_manager, settings_plane)

        self.ui_elements["texture_selection"] = texture_selection
        self.ui_elements["texture_current"] = texture_current

        # Spielfeldgröße
        size_text_rect = pygame.Rect(200, 203, 150, 50)
        size_inputfiled1_rect = pygame.Rect(200, 200, 150, 50)
        size_inputfiled2_rect = pygame.Rect(200, 200, 150, 50)
        size_text_rect, size_inputfiled1_rect, size_inputfiled2_rect = center_objects(size_text_rect,
                                                                                      size_inputfiled1_rect,
                                                                                      size_inputfiled2_rect,
                                                                                      center_y=450)
        gamesize_textbox = pygame_gui.elements.UILabel(size_text_rect, "Spielfeldgröße:", self.ui_manager, settings_plane)

        self.ui_elements["gamesize_textbox"] = gamesize_textbox

        gamesize_inputbox1 = pygame_gui.elements.UITextEntryLine(size_inputfiled1_rect, self.ui_manager,
                                                                 settings_plane)
        gamesize_inputbox1.set_text(str(self.settings.size[0])+" ")
        self.ui_elements["gamesize_inputbox1"] = gamesize_inputbox1

        gamesize_inputbox2 = pygame_gui.elements.UITextEntryLine(size_inputfiled2_rect, self.ui_manager,
                                                                 settings_plane)
        gamesize_inputbox2.set_text(str(self.settings.size[1])+" ")
        self.ui_elements["gamesize_inputbox2"] = gamesize_inputbox2

        # Speichern/Schließen
        save_rect = pygame.Rect(200, 300, 150, 50)
        quit_rect = pygame.Rect(400, 300, 150, 50)
        save_rect, quit_rect = center_objects(save_rect, quit_rect, center_y=530)  # center objects

        save = pygame_gui.elements.UIButton(save_rect, "Speichern", self.ui_manager, settings_plane)
        self.ui_elements["save"] = save
        quit_settings = pygame_gui.elements.UIButton(quit_rect, "Schließen", self.ui_manager, settings_plane)
        self.ui_elements["quit_settings"] = quit_settings

    def setup_ui(self):
        # Die Elemente der Benutzeroberfläche werden in einem Dictonary gespeichert um mit weniger Variablen
        # umzugehen zu müssen
        self.ui_elements = {}
        self.ui_manager = pygame_gui.ui_manager.UIManager(MAINSCREEN_SIZE, "gametheme.json")

        # Fonts laden
        self.ui_manager.preload_fonts([{'name': 'fira_code', 'point_size': 14, 'style': 'bold'}])
        # Hauptmenü erstellen
        self.setup_main_plane()
        # Einstellungsmenü erstellen
        self.setup_settings_plane()
        # Hauptmenü soll angezeigt werden
        self.ui_elements.get("main_plane").show()
        self.ui_elements.get("settings_plane").hide()

        if self.logging:
            self.logger.info("setup_ui called")

    def events(self):
        for event in pygame.event.get():

            if event.type == pygame.QUIT:  # Fenster soll geschlossen werden
                self.running = False

            if event.type == pygame_gui.UI_BUTTON_PRESSED: # Event von pygame_gui

                if event.ui_element == self.ui_elements.get("start"):  # Startknopf wurde gedrückt
                    try:
                        self.screen, quit_ = game.run(self.get_curgamemode(), MAINSCREEN_SIZE, self.logger_file, self.logging_lvl)
                    except Exception as e: # Fehler während der Ausführung des Spiels
                        from traceback import format_exc
                        if self.logging:
                            self.logger.critical(f"Game crashed; Exception: {str(e)}, traceback: {format_exc()}")
                        self.screen = resize(MAINSCREEN_SIZE) # Stellt sicher, das self.screen die richtige Größe hat
                    else: # Wird ausgeführt, wenn es jeine Exception gab
                        if quit_ is True: # Gesamtes Programm soll beendet werden
                            if self.logging:
                                self.logger.info("going to quit pygame and call 'exit(1)'")
                            self.running = False
                            pygame.quit()
                            exit(0) # beendet das Programm sofort

                elif event.ui_element == self.ui_elements.get("main_close_button"):  # Schließenknopf wurde gedrückt
                    self.running = False

                elif event.ui_element == self.ui_elements.get("settings"):  # Einstellungsknopf wurde gedrückt
                    self.ui_elements.get("settings_plane").show()
                    self.ui_elements.get("main_plane").hide()
                    if self.logging:
                        self.logger.info("showing settings menu")

                elif event.ui_element == self.ui_elements.get("quit_settings"): # Einstellungen-Verlassen-Knopf wurde gedrückt
                    self.ui_elements.get("settings_plane").hide()
                    self.ui_elements.get("main_plane").show()
                    if self.logging:
                        self.logger.info("showing main menu")

                elif event.ui_element == self.ui_elements.get("save"): # Einstellungen-Speichern-Knopf wurde gedrückt
                    self.save()
                elif event.ui_element == self.ui_elements.get("gamemode_subsettings_button"):
                    self.ui_elements.get("settings_plane").hide()
                    self.get_curgamemode().set_subsettings_visibility(True)
                elif self.get_curgamemode().isquit(event.ui_element):
                    self.ui_elements.get("settings_plane").show()
                    self.get_curgamemode().set_subsettings_visibility(False)
            self.ui_manager.process_events(event)

    def run(self) -> None:
        # screen_size = MAINSCREEN_SIZE

        self.running = True
        while self.running:
            # gibt die sogenannte 'Deltatime' zurück (Zeit zwischen zwei Aufrufen)
            # /1000 damit man die Sekunden hat
            deltatime = self.clock.tick(self.settings.fps) / 1000

            self.events()

            self.ui_manager.update(deltatime)
            self.ui_manager.draw_ui(self.screen)

            # Aktualisiert den Bildschirm
            pygame.display.flip()
        pygame.quit()

    def save(self) -> None:
        if self.logging:
            self.logger.info("save called")

        # SubSettings speichern
        self.get_curgamemode().save(self.logger if self.logging else None)

        # Spielfeldgröße
        try:
            width = int(self.ui_elements.get("gamesize_inputbox1").get_text().strip(" "))
            height = int(self.ui_elements.get("gamesize_inputbox2").get_text().strip(" "))
        except ValueError: # Mindestens ein Text in einem der Eingabefelder kann nicht in eine Ganzahl umgewandelt werden
            if self.logging:
                self.logger.warning(f"Wrong Value for width ({self.ui_elements.get('gamesize_inputbox1').get_text().strip(' ')}) or height ({self.ui_elements.get('gamesize_inputbox2').get_text().strip(' ')})")
            # Werte werden zurückgesetzt auf die vor der Veränderung
            self.ui_elements.get("gamesize_inputbox1").set_text(str(self.settings.size[0])+" ")
            self.ui_elements.get("gamesize_inputbox2").set_text(str(self.settings.size[1])+" ")
        else: # Wird nur ausgeführt, wenn es keine Exception gab
            if width < 4 or height < 4: # 4 ist die Mindestgröße
                # Werte werden zurückgesetzt auf die vor der Veränderung
                self.ui_elements.get("gamesize_inputbox1").set_text(str(self.settings.size[0])+" ")
                self.ui_elements.get("gamesize_inputbox2").set_text(str(self.settings.size[1])+" ")
                pygame_gui.windows.ui_message_window.UIMessageWindow(center_object(pygame.Rect(0, 0, 300, 200), resulution=MAINSCREEN_SIZE), "Das Spielfeld muss jeweils größer als 3 sein. Deswegen wurde es zurückgesetzt.", self.ui_manager)

                if self.logging:
                    self.logger.debug(f"Given width ({width}) and/or height ({height}) to low (<4)")
            else:
                self.settings.size = [width, height]

        # Spielmodus
        selection_list: pygame_gui.elements.ui_selection_list.UISelectionList = self.ui_elements.get("gamemode_selection")
        selected = selection_list.get_single_selection()
        if selected is not None: # Es wurde ein Spielmodus gewählt
            gamemode_text: pygame_gui.elements.UILabel = self.ui_elements.get("gamemode_current")
            gamemode_text.set_text(f"Spielmodus: {selected}")
            self.settings.gamemode = selected # Ausgewählter Spielmodus wird gespeichert
        elif self.logging:
            self.logger.debug("no gamemode selected")

        # Schlangengeschwindigkeit
        speed = self.ui_elements.get("snakespeed_input").get_text().replace(",", ".")
        try:
            speed = float(speed)
            if speed <= 0:
                raise ValueError
        except ValueError: # Der Inhalt des Eingabefelds ist keine Zahl (und kann entsprechend nicht konvertiert werden)
            self.ui_elements.get("snakespeed_input").set_text(str(self.settings.snakespeed))
            if self.logging:
                self.logger.warning(f"Given snakespeed input is invalid ({speed})")
        else:
            # Wird ausgeführt wenn es keinen Error gibt
            self.settings.snakespeed = speed

        # Texturen
        selection_list = self.ui_elements.get("texture_selection")
        selected = selection_list.get_single_selection()
        if selected is not None:
            texture_text = self.ui_elements.get("texture_current")
            texture_text.set_text(f"Texturen: {selected}")
            self.settings.texturepack = selected
        elif self.logging:
            self.logger.debug("No texture selected")

        # Anpassung des 'gamemode_subsettings_button'
        if self.get_curgamemode().has_subsettings:
            self.ui_elements.get("gamemode_subsettings_button").enable()
        else:
            self.ui_elements.get("gamemode_subsettings_button").disable()

        if self.logging:
            self.logger.debug(f"new settings: {self.settings.content}")

def center(object_, resolution: Tuple[int, int] = MAINSCREEN_SIZE):
    object_width = object_.width if hasattr(object_, "width") else object_.get_width() # Weite des Objekts
    object_height = object_.height if hasattr(object_, "height") else object_.get_height() # Höhe des Objekts

    # - Weite/Höhe ist nötig um die Oberstlinke Position zu erhalten
    topleft_x = (resolution[0] - object_width) // 2
    topleft_y = (resolution[1] - object_height) // 2
    return [topleft_x, topleft_y]

def center_object(object_, center_x=True, center_y = True, resulution: Tuple[int, int] = MAINSCREEN_SIZE,
                  offset_x:int = 0, offset_y: int = 0):
    """
    Funktioniert identisch zu 'center' mit dem Unterschied, das es mehr optionen gibt
    """
    topleft = object_.topleft # alte Position wird gespeichert
    positions = center(object_, resulution)
    positions[0] += offset_x
    positions[1] += offset_y

    # Zurücksetzen von Positionen
    if not center_x:
        positions[0] = topleft[0]

    if not center_y:
        positions[1] = topleft[1]

    object_.topleft = tuple(positions)
    return object_

def center_objects(*objects, center_x: Union[bool, int] = True, center_y: Union[bool, int] = False, resolution: Tuple[int, int] = MAINSCREEN_SIZE):
    if center_x is True:
        free_size_x = resolution[0]  # Platz der auf der x-Achse frei ist
        for obj in objects:
            free_size_x -= obj.width

        space_value_x = free_size_x // (len(objects) + 1) # Platz zwischen jedem Objekt auf der x-Achse

        for index, obj in enumerate(objects):
            if index == 0:
                obj.topleft = (space_value_x, obj.topleft[1])
            else:
                # neue x-Position:  Obenlinke x-position des Vorangegangenen Objekts + die Weite dieses Objekts + der freie Platz zwischen jedem Objekt
                obj.topleft = (objects[index-1].topleft[0] + objects[index-1].width + space_value_x, obj.topleft[1])

    elif isinstance(center_x, int): # Der Mittelpunkt der Objekte wird auf der x-Achse zu'center_x' gesetzt

        for index, obj in enumerate(objects):
            obj.center = (center_x, obj.center[1])

    if center_y is True:
        free_size_y = resolution[1] # Platz der auf der y-Achse frei ist
        for obj in objects:
            free_size_y -= obj.height

        space_value_y = free_size_y // (len(objects) + 1) # Platz zwischen jedem Objekt auf der y-Achse

        for index, obj in enumerate(objects):
            if index == 0:
                obj.topleft = (obj.topleft[0], space_value_y)
            else:
                # neue y-Position:  Obenlinke y-position des Vorangegangenen Objekts + die Höhe dieses Objekts + der freie Platz zwischen jedem Objekt
                obj.topleft = (obj.topleft[0], objects[index-1].topleft[1] + objects[index-1].height + space_value_y)

    elif isinstance(center_y, (int, float)): # Der Mittelpunkt der Objekte wird auf der y-Achse zu'center_y' gesetzt
        for index, obj in enumerate(objects):
            obj.center = (obj.center[0], center_y)
    return objects

def resize(size, surface=None) -> pygame.Surface:
    if surface is None:
        screen = pygame.display.set_mode(size) # gibt ein pygame.Surface zurück, welches das Spielfenster darstellt
    else:
        screen = pygame.transform.scale(surface, size)
    return screen

if __name__ == "__main__": # ist nur Wahr, wenn main.py direkt aufgerufen wurde (nicht importiert)
    # Standardargumente
    log = False
    lvl = logging.DEBUG # lvl = 10

    # Überprüfen der übergebenen Argumente auf den Text "debug" und eine Zahl
    if len(argv) >= 2 and argv[1].lower() == "debug":
        log = True
        if len(argv) >= 3:
            lvl = int(argv[2])*10   # DEBUG ist im logging modul eigentlich 10, INFO 20
                                    # so müssen nur 1,2,3,4 oder 5 eingegeben werden um ein Level zu setzen
    MainMenu(logging_=log, lvl=lvl).run() # startet das Programm

    # INFO:
    #   Interpreter: CPython 3.7.9
    #   pygame 2.0.1
    #   pygame_gui 0.6.4
