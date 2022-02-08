from typing import Tuple, Union

import pygame
import pygame_gui
#from pygame.color import THECOLORS

import game
from settings import Settings


MAINSCREEN_SIZE = (800, 400)
TILE_SIZE = (20, 20)
# FPS = 60

# STANDARD_GAME_SIZE = (800, 600)

class MainMenu:
    def __init__(self, settings: Settings = None):
        # Pygame initialisieren
        pygame.init()
        pygame.font.init()

        # Einstellungen
        if settings is None:
            settings = Settings(autosave=True)
        self.settings = settings

        pygame.display.set_caption("Snake")

        self.clock = pygame.time.Clock()
        self.screen = resize(MAINSCREEN_SIZE)

        # Benutzeroberfläche erstellen
        self.setup_ui()

        self.running = False

    def setup_main_plane(self):
        # main plane
        main_plane = pygame_gui.elements.ui_panel.UIPanel(pygame.Rect(0, 0, *MAINSCREEN_SIZE), 0, self.ui_manager, visible=0)
        self.ui_elements["main_plane"] = main_plane

        settings = pygame_gui.elements.UIButton(
            relative_rect=center_object(pygame.Rect(200, 200, 200, 50), center_y=False),
            text="Einstellungen",
            manager=self.ui_manager,
            container=main_plane,
            visible=0)
        self.ui_elements["settings"] = settings

        start = pygame_gui.elements.UIButton(
            relative_rect=center_object(pygame.Rect(200, 100, 200, 50), center_y=False),
            text="Start",
            manager=self.ui_manager,
            container=main_plane,
            visible=0)
        self.ui_elements["start"] = start

        snake_title_text = pygame_gui.elements.UITextBox("<b>Snake Game<b>",
                                                         center_object(pygame.Rect(220, 40, 100, -1),
                                                                                     center_y=False, offset_x=50),
                                                         manager=self.ui_manager,
                                                         container=main_plane,
                                                         visible=0,
                                                         wrap_to_height=True
                                                         )
        self.ui_elements["snake_title_text"] = snake_title_text

        main_close_button = pygame_gui.elements.UIButton(
            relative_rect=center_object(pygame.Rect(200, 300, 200, 50), center_y=False),
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

        # Oberfläche für die Spielgröße
        size_text_rect = pygame.Rect(200, 203, 150, 50)
        size_inputfiled1_rect = pygame.Rect(200, 200, 150, 50)
        size_inputfiled2_rect = pygame.Rect(200, 200, 150, 50)
        size_text_rect, size_inputfiled1_rect, size_inputfiled2_rect = center_objects(size_text_rect,
                                                                                      size_inputfiled1_rect,
                                                                                      size_inputfiled2_rect,
                                                                                      center_y=250)
        # Spielmodus
        gamemode_current_rect = pygame.Rect(200, 100, 200, 50)
        gamemode_selection_rect = pygame.Rect(200, 100, 150, 66)
        gamemode_current_rect, gamemode_selection_rect = center_objects(gamemode_current_rect, gamemode_selection_rect, center_y=150)
        gamemode_selection = pygame_gui.elements.ui_selection_list.UISelectionList(gamemode_selection_rect,
                                                                                  ["Normal", "Kopftausch", "Wandlos"],
                                                                                  self.ui_manager,
                                                                                  container=settings_plane)
        gamemode_current = pygame_gui.elements.UILabel(gamemode_current_rect,
                                                       f"Spielmodus: {map_gamemode(self.settings.gamemode)}",
                                                       self.ui_manager, settings_plane)

        self.ui_elements["gamemode_selection"] = gamemode_selection
        self.ui_elements["gamemode_current"] = gamemode_current

        # Spielfeldgröße
        gamesize_textbox = pygame_gui.elements.UILabel(size_text_rect, "Spielfeldgröße:", self.ui_manager, settings_plane)

        self.ui_elements["gamesize_textbox"] = gamesize_textbox

        gamesize_inputbox1 = pygame_gui.elements.UITextEntryLine(size_inputfiled1_rect, self.ui_manager,
                                                                 settings_plane)
        gamesize_inputbox1.set_text(str(self.settings.size[0]))
        self.ui_elements["gamesize_inputbox1"] = gamesize_inputbox1

        gamesize_inputbox2 = pygame_gui.elements.UITextEntryLine(size_inputfiled2_rect, self.ui_manager,
                                                                 settings_plane)
        gamesize_inputbox2.set_text(str(self.settings.size[1]))
        self.ui_elements["gamesize_inputbox2"] = gamesize_inputbox2

        # Speichern/Schließen
        save_rect = pygame.Rect(200, 300, 150, 50)
        quit_rect = pygame.Rect(400, 300, 150, 50)
        save_rect, quit_rect = center_objects(save_rect, quit_rect, center_y=350)  # center objects

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

    def events(self):
        for event in pygame.event.get():

            if event.type == pygame.QUIT:  # Fenster soll geschlossen werden
                self.running = False

            if event.type == pygame_gui.UI_BUTTON_PRESSED:

                if event.ui_element == self.ui_elements.get("start"):  # Startknopf wurde gedrückt
                    self.screen = game.run(self.settings, MAINSCREEN_SIZE)

                elif event.ui_element == self.ui_elements.get("main_close_button"):  # Schließenknopf wurde gedrückt
                    self.running = False

                elif event.ui_element == self.ui_elements.get("settings"):  # Einstellungsknopf wurde gedrückt
                    self.ui_elements.get("settings_plane").show()
                    self.ui_elements.get("main_plane").hide()

                elif event.ui_element == self.ui_elements.get("quit_settings"): # Einstellungen-Verlassen-Knopf wurde gedrückt
                    self.ui_elements.get("settings_plane").hide()
                    self.ui_elements.get("main_plane").show()

                elif event.ui_element == self.ui_elements.get("save"): # Einstellungen-Speichern-Knopf wurde gedrückt
                    self.save()

            self.ui_manager.process_events(event)

    def run(self) -> None:
        # screen_size = MAINSCREEN_SIZE

        self.running = True
        while self.running:
            # gibt die sogenannte 'Deltatime' zurück
            # /1000 damit man die Sekunden hat
            deltatime = self.clock.tick(self.settings.fps) / 1000

            self.events()

            self.ui_manager.update(deltatime)
            self.ui_manager.draw_ui(self.screen)

            # Aktualisiert den Bildschirm
            pygame.display.flip()

    def save(self) -> None:

        # Spielfeldgröße
        width = int(self.ui_elements.get("gamesize_inputbox1").get_text())
        height = int(self.ui_elements.get("gamesize_inputbox2").get_text())
        if width % TILE_SIZE[0] != 0 or height % TILE_SIZE[1]:  # Wenn die eingegebene Größe nicht passt
            self.ui_elements.get("gamesize_inputbox1").set_text(str(self.settings.size[0]))
            self.ui_elements.get("gamesize_inputbox2").set_text(str(self.settings.size[1]))
            pygame_gui.windows.ui_message_window.UIMessageWindow(center_object(pygame.Rect(0, 0, 100, 100), resulution=self.settings.size), "Invalid Gamesize", self.ui_manager)
        else:
            self.settings.size = [width, height]

        # Spielmodus
        selection_list: pygame_gui.elements.ui_selection_list.UISelectionList = self.ui_elements.get("gamemode_selection")
        selected = selection_list.get_single_selection()
        if selected is not None:
            gamemode_text: pygame_gui.elements.UILabel = self.ui_elements.get("gamemode_current")
            gamemode_text.set_text(f"Spielmodus: {selected}")
            self.settings.gamemode = map_gamemode(selected)

        # Schlangengeschwindigkeit
        speed = self.ui_elements.get("snakespeed_input").get_text()
        try:
            speed = float(speed)
        except ValueError:
            self.ui_elements.get("snakespeed_input").set_text(str(self.settings.snakespeed))
        else:
            # Wird ausgeführt wenn es keinen Error gibt
            self.settings.snakespeed = speed

def center(object_, resolution: Tuple[int, int] = MAINSCREEN_SIZE):
    object_width = object_.width if hasattr(object_, "width") else object_.get_width()
    object_height = object_.height if hasattr(object_, "height") else object_.get_height()

    topleft_x = (resolution[0] - object_width) // 2
    topleft_y = (resolution[1] - object_height) // 2
    return [topleft_x, topleft_y]

def center_object(object_, center_x=True, center_y = True, resulution: Tuple[int, int] = MAINSCREEN_SIZE,
                  offset_x:int = 0, offset_y: int = 0):
    topleft = object_.topleft
    positions = center(object_, resulution)
    positions[0] += offset_x
    positions[1] += offset_y
    if not center_x:
        positions[0] = topleft[0]

    if not center_y:
        positions[1] = topleft[1]

    object_.topleft = tuple(positions)
    return object_

def center_objects(*objects, center_x: Union[bool, int] = True, center_y: Union[bool, int] = False, resolution: Tuple[int, int] = MAINSCREEN_SIZE):
    if center_x is True:
        free_size_x = resolution[0]
        for obj in objects:
            free_size_x -= obj.width

        space_value_x = free_size_x // (len(objects) + 1)

        for index, obj in enumerate(objects):
            if index == 0:
                obj.topleft = (space_value_x, obj.topleft[1])
            else:
                obj.topleft = (objects[index-1].topleft[0] + objects[index-1].width + space_value_x, obj.topleft[1])

    elif isinstance(center_x, int):

        for index, obj in enumerate(objects):
            obj.topleft = (center_x - obj.width // 2, obj.topleft[1])

    if center_y is True:
        free_size_y = resolution[1]
        for obj in objects:
            free_size_y -= obj.height

        space_value_y = free_size_y // (len(objects) + 1)

        for index, obj in enumerate(objects):
            if index == 0:
                obj.topleft = (obj.topleft[0], space_value_y)
            else:
                obj.topleft = (obj.topleft[0], objects[index-1].topleft[1] + objects[index-1].height + space_value_y)

    elif isinstance(center_y, (int, float)):
        for index, obj in enumerate(objects):
            obj.topleft = (obj.topleft[0], center_y - obj.height//2)
    return objects

def resize(size, surface=None) -> pygame.Surface:
    if surface is None:
        screen = pygame.display.set_mode(size)
    else:
        screen = pygame.transform.scale(surface, size)
    return screen

def map_gamemode(name: str) -> str:
    """
    Gibt zu dem Spielmodus-Namen den passende bezeichnung in den Einstellungen zurück und vise versa
    """
    sett_to_name = {"default": "Normal", "no_walls": "Wandlos", "switching_head": "Kopftausch"}
    name_to_sett = {"Normal": "default", "Wandlos": "no_walls", "Kopftausch": "switching_head"}
    if name in sett_to_name.keys():
        return sett_to_name.get(name)
    elif name in name_to_sett.keys():
        return name_to_sett.get(name)
    else:
        raise Exception("gave a wrong name")

if __name__ == "__main__":
    MainMenu().run() # startet das Programm
    # main()
