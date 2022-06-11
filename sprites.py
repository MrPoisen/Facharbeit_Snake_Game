# Standardbibliothek
from typing import Dict, List, Tuple
from enum import Enum, auto
import os
from glob import iglob

# externe Bibliothek
import pygame
from pygame.color import THECOLORS
from pygame.locals import (
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_w,
    K_s,
    K_a,
    K_d
  )

# lokale Module
from settings import Settings
#from main import TILE_SIZE

# KONSTANTEN (hier sind es Farben)
MAINCOLOR = THECOLORS.get("darkgreen")
EDGECOLOR = THECOLORS.get("green")

class Direction(Enum):
    UP = auto()
    RIGHT = auto()
    DOWN = auto()
    LEFT = auto()

    @staticmethod
    def invert(direction: "Direction"):
        """Gibt die enteggengesetzte Richtung zurück"""
        if direction == Direction.UP:
            return Direction.DOWN
        elif direction == Direction.RIGHT:
            return Direction.LEFT
        elif direction == Direction.DOWN:
            return Direction.UP
        elif direction == Direction.LEFT:
            return Direction.UP
        else:
            raise Exception("Es wurde keine Richtung ('Direction') gegeben")

class TexturePack:
    def __init__(self, folder, settings: Settings):
        pygame.display.init()
        self._settings = settings
        self.folder = folder
        self._textures: Dict[str, pygame.Surface] = {}
        self.drawbackground = None

        self.snakeedge_height = 1

        self._load()
        self.rescale(self._settings.tilesize)

    @property
    def name(self):
        return self.folder

    @staticmethod
    def texturpacks():
        return [os.path.basename(folder) for folder in iglob("textures\\*")]

    def _load(self):
        import importlib
        from types import MethodType
        path_to_files = f"textures\\{self.folder}\\"
        for filename in iglob(f"{path_to_files}*.png"):
            basename = os.path.basename(filename)[:-4].upper()
            with open(filename) as file:
                picture = pygame.image.load(file)
            if basename == "SNAKEEDGE":
                picture = pygame.transform.scale(picture.convert_alpha(), (self._settings.tilesize[0], self.snakeedge_height))
            else:
                picture = pygame.transform.scale(picture.convert_alpha(), self._settings.tilesize)
            self._textures[basename] = picture # [:-4] entfernt .png

        if os.path.exists(f"{path_to_files}background.py"):
            # background.py wird geladen
            module_path = os.path.abspath(f"{path_to_files}background.py")
            spec = importlib.util.spec_from_file_location("background", module_path)
            background = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(background)
            if hasattr(background, "draw"):
                self.drawbackground = MethodType(background.draw, self)

        if self.drawbackground is None:
            self.drawbackground = self._default_drawbackground

        self._textures["BACKGROUND"] = self.drawbackground()

    def _default_drawbackground(self) -> pygame.Surface:
        if "BACKGROUND1" in self._textures.keys() and "BACKGROUND2" in self._textures.keys():
            draw1 = lambda surface, rect: surface.blit(self._textures["BACKGROUND1"], rect)
            draw2 = lambda surface, rect: surface.blit(self._textures["BACKGROUND2"], rect)
        else:
            draw1 = lambda surface, rect: pygame.draw.rect(surface, (30, 30, 30, 100),  # Farbe ist ein dunkles Grau
                             rect)
            draw2 = lambda surface, rect: pygame.draw.rect(surface, THECOLORS.get("black"),
                             rect)

        surface = pygame.Surface(self._settings.realsize)
        for i in range(self._settings.size[0]): # x-Achse
            for ii in range(self._settings.size[1]): # y-Achse
                rect = pygame.Rect(i * self._settings.tilesize[0], ii * self._settings.tilesize[1], *self._settings.tilesize)
                if (i % 2 == 0 and ii % 2 == 0) or (i % 2 != 0 and ii % 2 != 0):
                    draw1(surface, rect)
                else:
                    draw2(surface, rect)
        return surface

    def rescale(self, scale: Tuple[int, int]):
        for name, surface in self._textures.items():
            if name == "SNAKEEDGE":
                self._textures[name] = pygame.transform.scale(surface, (scale[0], self.snakeedge_height))
            else:
                self._textures[name] = pygame.transform.scale(surface, scale)
        self._textures["BACKGROUND"] = self.drawbackground()


    def isfull(self):
        for surf_name in ("APPLE", "SNAKEHEAD", "SNAKEHEAD", "SNAKEEDGE", "BACKGROUND"):
            if surf_name not in self._textures.keys():
                return False
        return True

    def create_edges(self, surf: pygame.Surface, top=True, right=True, bottom=True, left=True) -> pygame.Surface:
        if top:
            surf.blit(self.snakeedge, (0, 0, self._settings.tilesize[0]-self.snakeedge_height, 0))
        if right:
            surf.blit(pygame.transform.rotate(self.snakeedge, 270), (self._settings.tilesize[0]-self.snakeedge_height, 0, self._settings.tilesize[0]-self.snakeedge_height, self._settings.tilesize[1]-self.snakeedge_height))
        if bottom:
            surf.blit(pygame.transform.rotate(self.snakeedge, 180), (0, self._settings.tilesize[1]-self.snakeedge_height, self._settings.tilesize[0]-self.snakeedge_height, self._settings.tilesize[1]-self.snakeedge_height))
        if left:
            surf.blit(pygame.transform.rotate(self.snakeedge, 90), (0, 0, 0, self._settings.tilesize[1]-self.snakeedge_height))
        return surf

    @property
    def apple(self):
        return self._textures.get("APPLE")

    @property
    def snakehead(self):
        return self._textures.get("SNAKEHEAD").copy()

    @property
    def snakebody(self):
        return self._textures.get("SNAKEBODY").copy()

    @property
    def snakeedge(self):
        return self._textures.get("SNAKEEDGE")

    @property
    def background(self):
        return self._textures.get("BACKGROUND")

class Apple(pygame.sprite.Sprite):
    def __init__(self, position: tuple, texturepack: TexturePack):
        super(Apple, self).__init__()
        self.texturepack = texturepack
        #self.surf = texturepack.apple
        #self.surf.fill(THECOLORS.get("red"))
        self.rect = self.texturepack.apple.get_rect()
        self.rect.topleft = position

    def draw(self, surface: pygame.Surface):
        surface.blit(self.texturepack.apple, self.rect)

    def rescale(self, size):
        # Hier muss nichts passieren
        pass

class SnakeHead(pygame.sprite.Sprite):
    def __init__(self, texturepack: TexturePack):
        super(SnakeHead, self).__init__()
        self.texturepack = texturepack
        self.surf = self.texturepack.snakehead

        self.rect = self.surf.get_rect() # Die Schlange startet oben links
        self.direction = Direction.RIGHT
        self._lastdirection = self.direction
        self.edges = {"top":True, "right":True, "bottom":True, "left":True} # Welche Kanten gezeichnet werden soll
        self.tails: List[Tail] = [] # Der Schlangenschwanz

        # Gruppen
        self.tail_group = None
        self.all_group = None

    def draw(self, surface: pygame.Surface):
        surface.blit(self.surf, self.rect)

    def rescale(self, size: Tuple[int, int]):
        self.surf = pygame.transform.scale(self.surf, size)

    def next_pos(self, move_value: Tuple[int, int] = (20, 20)) -> pygame.sprite.Sprite:
        """Gibt die nächste Position der Schlange als Sprite Objekt zurück"""
        move_x = 0
        move_y = 0
        if self.direction == Direction.RIGHT:
            move_x = move_value[0]
        elif self.direction == Direction.LEFT:
            move_x = -move_value[0]  # moves left
        elif self.direction == Direction.UP:
            move_y = -move_value[1]
        elif self.direction == Direction.DOWN:
            move_y = move_value[1]  # moves Down

        sprite = pygame.sprite.Sprite() # sprite dient als dummy
        sprite.rect = self.rect.move(move_x, move_y)
        return sprite

    def make_surf(self, top=True, right=True, bottom=True, left=True) -> None: # Generiert die Darstellung für den Schlangenkopf
        self.edges = {"top": top, "right": right, "bottom": bottom, "left": left}
        self.surf = self.texturepack.create_edges(self.texturepack.snakehead, top, right, bottom, left)

    def accept_direction(self, pressed_keys: dict) -> None:
        """Überprüft die übergebenen gedrückten Knöpfe und ändert gegebenenfalls die Richtung der Schlange"""
        if (pressed_keys[K_UP] or pressed_keys[K_w]) and self._lastdirection != Direction.DOWN:
            self.direction = Direction.UP
        if (pressed_keys[K_DOWN] or pressed_keys[K_s]) and self._lastdirection != Direction.UP:
            self.direction = Direction.DOWN
        if (pressed_keys[K_LEFT] or pressed_keys[K_a]) and self._lastdirection != Direction.RIGHT:
            self.direction = Direction.LEFT
        if (pressed_keys[K_RIGHT] or pressed_keys[K_d]) and self._lastdirection != Direction.LEFT:
            self.direction = Direction.RIGHT

    def update(self, collide_with_apple: bool = False, texture: bool = True) -> None:
        self._lastdirection = self.direction  # verhindert illegale Bewegung
        old_topleft = self.rect.topleft

        # Schlangenkopf wird bewegt
        next_pos_rect = self.next_pos(self.texturepack._settings.tilesize).rect  # Bewegt 'rect'
        self.rect.update(next_pos_rect.left, next_pos_rect.top, self.rect.width, self.rect.height)

        if collide_with_apple:  # Fügt das Tail objekt hinzu; Die Position entspricht die der alten Schlangenkopfposition
            tail = Tail(old_topleft, self.direction, self.texturepack)
            self.tails.insert(0, tail)
            self.tail_group.add(tail)
            self.all_group.add(tail)

        else:  # Alle Tails werden bewegt
            old_directions = []
            for tail in self.tails:
                tail.update() # Bewegt das Tail objekt
                old_directions.append(tail.direction)
            old_directions.insert(0, self.direction) # Fügt den Kopf hinzu
            old_directions.pop() # Entfernt das letzte Element, da es nicht gebraucht wird
            for tail, old_direction in zip(self.tails, old_directions):
                tail.direction = old_direction

        if texture:
            self.texture(full=collide_with_apple)

    def texture(self, settings: Settings = None, full: bool = False):
        if len(self.tails) == 0:
            self.make_surf()
            return
        top = bottom = left = right = True
        if self.direction == Direction.UP:
            self.make_surf(bottom=False)
            top = False
        elif self.direction == Direction.RIGHT:
            self.make_surf(left=False)
            right = False
        elif self.direction == Direction.DOWN:
            self.make_surf(top=False)
            bottom = False
        elif self.direction == Direction.LEFT:
            self.make_surf(right=False)
            left = False

        # erster Schlangenteil
        if not len(self.tails) > 1:
            self.tails[0].make_surf(top, right, bottom, left)
            return

        tails = [self, *self.tails]
        last = len(self.tails)-1 # Index des Letzten Schwanzteils
        for index in range(len(self.tails)-1, -1, -1): # iteriert Rückwärts über die Indexe
            if full or index in {0, last}:
                self._full_render(tails, self.tails[index], index+1, settings)
            else:
                # Die neue Textur entspricht die des vorangegangenen Objektes
                self.tails[index].make_surf(**self.tails[index-1].edges)

    def _full_render(self, tails: List["Tail"], tail: "Tail", index: int, settings: Settings = None):
        """Generiert die Textur für ein bestimmtes Tail Objekt"""
        top = bottom = left = right = True
        tilesize = self.texturepack._settings.tilesize
        realsize = self.texturepack._settings.realsize

        # Überprüft in welcher Richtung das vorangegangene Tail-Objekt relativ zum jetzigen ist
        if (tail.rect.topleft[0] - tilesize[0] == tails[index - 1].rect.topleft[0]):
            left = False
        elif (tail.rect.topleft[0] + tilesize[0] == tails[index - 1].rect.topleft[0]):
            right = False
        elif (tail.rect.topleft[1] - tilesize[1] == tails[index - 1].rect.topleft[1]):
            top = False
        elif (tail.rect.topleft[1] + tilesize[1] == tails[index - 1].rect.topleft[1]):
            bottom = False
        if index + 1 < len(tails):
            # Überprüft in welcher Richtung das nächste Tail-Objekt relativ zum jetzigen ist
            if tail.rect.topleft[0] - tilesize[0] == tails[index + 1].rect.topleft[0]:
                left = False
            elif tail.rect.topleft[0] + tilesize[0] ==  tails[index + 1].rect.topleft[0]:
                right = False
            elif tail.rect.topleft[1] - tilesize[1] == tails[index + 1].rect.topleft[1]:
                top = False
            elif tail.rect.topleft[1] + tilesize[1] == tails[index + 1].rect.topleft[1]:
                bottom = False

        if settings is not None: # ist wichtig für den Wandlos Spielmodus
            if index+1 < len(tails) and tail.rect.topleft[0] == 0 and tails[index+1].rect.topleft[0] == realsize[0]-tilesize[0]:
                left = False
            elif index+1 < len(tails) and tail.rect.topleft[0] == realsize[0]-tilesize[0] and tails[index+1].rect.topleft[0] == 0:
                right = False
            elif tail.rect.topleft[0] == realsize[0]-tilesize[0] and tails[index-1].rect.topleft[0] == 0:
                right = False
            elif tail.rect.topleft[0] == 0 and tails[index-1].rect.topleft[0] == realsize[0]-tilesize[0]:
                left = False
            elif index+1 < len(tails) and tail.rect.topleft[1] == 0 and tails[index+1].rect.topleft[1] == realsize[1]-tilesize[1]:
                top = False
            elif index+1 < len(tails) and tail.rect.topleft[1] == realsize[1]-tilesize[1] and tails[index+1].rect.topleft[1] == 0:
                bottom = False
            elif tail.rect.topleft[1] == realsize[1]-tilesize[1] and tails[index-1].rect.topleft[1] == 0:
                bottom = False
            elif tail.rect.topleft[1] == 0 and tails[index-1].rect.topleft[1] == realsize[1]-tilesize[1]:
                top = False

        tail.make_surf(top, right, bottom, left)

    def add_tail(self, tail):
        self.tails.append(tail)

    def update_direction(self): # Funktioniert nicht im Wandlosspielmodus (braucht es auch nicht)
        """Generiert die Richtungen für die Schlange und die Tails basierend auf ihren Positionen"""
        snake_rect = self.rect
        next_taile_rect = self.tails[0].rect

        if snake_rect.x > next_taile_rect.x:
            self.direction = Direction.RIGHT
            self._lastdirection = Direction.invert(Direction.RIGHT)  # kann man auch direkt Direction.LEFT hinschreiben
        elif snake_rect.x < next_taile_rect.x:
            self.direction = Direction.LEFT
            self._lastdirection = Direction.invert(Direction.LEFT)
        elif snake_rect.y > next_taile_rect.y:
            self.direction = Direction.DOWN
            self._lastdirection = Direction.invert(Direction.UP)
        elif snake_rect.y < next_taile_rect.y:
            self.direction = Direction.UP
            self._lastdirection = Direction.invert(Direction.DOWN)

        old_topleft = self.rect.topleft
        for index, tail in enumerate(self.tails):
            if old_topleft[0] > tail.rect.topleft[0]:  # Vorherige Position ist weiter rechts
                tail.direction = Direction.RIGHT
            elif old_topleft[0] < tail.rect.topleft[0]: # Vorherige Position ist weiter links
                tail.direction = Direction.LEFT
            elif old_topleft[1] > tail.rect.topleft[1]:  # Vorherige Position ist weiter unten
                tail.direction = Direction.DOWN
            else: # Vorherige Position ist weiter oben
                tail.direction = Direction.UP
            old_topleft = tail.rect.topleft


class Tail(pygame.sprite.Sprite):
    def __init__(self, position: tuple, direction: Direction, texturepack: TexturePack):
        super(Tail, self).__init__()
        self.texturepack = texturepack
        self.surf = self.texturepack.snakebody
        self.rect = self.surf.get_rect()
        self.rect.topleft = position

        self.direction = direction

    def draw(self, surface: pygame.Surface):
        surface.blit(self.surf, self.rect)

    def rescale(self, size: Tuple[int, int]):
        self.surf = pygame.transform.scale(self.surf, size)

    def update(self):
        # Bewegt sich
        step = self.texturepack._settings.tilesize
        if self.direction == Direction.UP:
            self.rect.move_ip(0, -step[1])
        elif self.direction == Direction.RIGHT:
            self.rect.move_ip(step[0], 0)
        elif self.direction == Direction.DOWN:
            self.rect.move_ip(0, step[1])
        elif self.direction == Direction.LEFT:
            self.rect.move_ip(-step[0], 0)

    def make_surf(self, top=True, right=True, bottom=True, left=True):
        """Erstellt die Textur"""
        self.edges = {"top": top, "right": right, "bottom": bottom, "left": left}
        self.surf = self.texturepack.create_edges(self.texturepack.snakebody, top, right, bottom, left)

if __name__ == "__main__":
    pygame.display.set_mode((100, 100))
    s = Settings()
    tp = TexturePack("default", s)
    print(TexturePack.texturpacks())
