# Standardbibliothek
from typing import List, Tuple
from enum import Enum, auto

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
from main import TILE_SIZE, resize

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

class Apple(pygame.sprite.Sprite):
    def __init__(self, position: tuple, size: tuple = (20, 20)):
        super(Apple, self).__init__()
        self.surf = pygame.Surface(size)
        self.surf.fill(THECOLORS.get("red"))
        self.rect = self.surf.get_rect()
        self.rect.topleft = position

class SnakeHead(pygame.sprite.Sprite):
    def __init__(self, size: tuple = (20, 20)):
        super(SnakeHead, self).__init__()
        self.surf = pygame.Surface(size)
        # Bild
        self.img: pygame.Surface = pygame.image.load("snakehead.png")
        self.img = resize((TILE_SIZE[0]-2, TILE_SIZE[1]-2), self.img) # stellt sicher, dass das Bild die richtige Größe hat

        self.rect = self.surf.get_rect(x=0, y=0) # Die Schlange startet oben links
        self.direction = Direction.RIGHT
        self._lastdirection = self.direction
        self.edges = {"top":True, "right":True, "bottom":True, "left":True} # Welche Kanten gezeichnet werden soll
        self.tails: List[Tail] = [] # Der Schlangenschwanz

        # Gruppen
        self.tail_group = None
        self.all_group = None

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
        self.surf.fill(MAINCOLOR)
        if top:
            pygame.draw.line(self.surf, EDGECOLOR, (0, 0), (TILE_SIZE[0]-1, 0))
        if right:
            pygame.draw.line(self.surf, EDGECOLOR, (TILE_SIZE[0]-1, 0), (TILE_SIZE[0]-1, TILE_SIZE[1]-1))
        if bottom:
            pygame.draw.line(self.surf, EDGECOLOR, (0, TILE_SIZE[1]-1), (TILE_SIZE[0]-1, TILE_SIZE[1]-1))
        if left:
            pygame.draw.line(self.surf, EDGECOLOR, (0, 0), (0, TILE_SIZE[1]-1))

        self.surf.blit(self.img, pygame.Rect(1,1,18,18))
        self.edges = {"top": top, "right": right, "bottom": bottom, "left": left}

    def accept_direction(self, pressed_keys) -> None:
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
        next_pos_rect = self.next_pos(TILE_SIZE).rect  # Bewegt 'rect'
        self.rect.update(next_pos_rect.left, next_pos_rect.top, self.rect.width, self.rect.height)

        if collide_with_apple:  # Fügt das Tail objekt hinzu; Die Position entspricht die der alten Schlangenkopfposition
            tail = Tail(old_topleft, self.direction, TILE_SIZE)
            self.tails.insert(0, tail)
            self.tail_group.add(tail)
            self.all_group.add(tail)

        else:  # Alle Tails werden bewegt
            old_directions = []
            for tail in self.tails:
                tail.update() # Bewegt das Tail objekt
                old_directions.append(tail.direction)
            old_directions.insert(0, self.direction)
            old_directions.pop()
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

    def _full_render(self, tails, tail, index, settings=None):
        """Generiert die Textur für ein bestimmtes Tail Objekt"""
        top = bottom = left = right = True

        # Überprüft in welcher Richtung das vorangegangene Tail-Objekt relativ zum jetzigen ist
        if (tail.rect.topleft[0] - TILE_SIZE[0] == tails[index - 1].rect.topleft[0]):
            left = False
        elif (tail.rect.topleft[0] + TILE_SIZE[0] == tails[index - 1].rect.topleft[0]):
            right = False
        elif (tail.rect.topleft[1] - TILE_SIZE[1] == tails[index - 1].rect.topleft[1]):
            top = False
        elif (tail.rect.topleft[1] + TILE_SIZE[1] == tails[index - 1].rect.topleft[1]):
            bottom = False
        if index + 1 < len(tails):
            # Überprüft in welcher Richtung das nächste Tail-Objekt relativ zum jetzigen ist
            if tail.rect.topleft[0] - TILE_SIZE[0] == tails[index + 1].rect.topleft[0]:
                left = False
            elif tail.rect.topleft[0] + TILE_SIZE[0] ==  tails[index + 1].rect.topleft[0]:
                right = False
            elif tail.rect.topleft[1] - TILE_SIZE[1] == tails[index + 1].rect.topleft[1]:
                top = False
            elif tail.rect.topleft[1] + TILE_SIZE[1] == tails[index + 1].rect.topleft[1]:
                bottom = False

        if settings is not None: # ist wichtig für den Wandlos Spielmodus
            if tail.direction is Direction.LEFT and tails[index-1].direction is tail.direction and tail.rect.topleft[0] == 0:
                left = False
            elif tail.direction is Direction.LEFT and (index+1 < len(tails) and tails[index+1].direction is tail.direction) and tail.rect.topleft[0] == settings.realsize[0]-TILE_SIZE[0]:
                right = False
            elif tail.direction is Direction.RIGHT and tails[index-1].direction is tail.direction and tail.rect.topleft[0] == settings.realsize[0]-TILE_SIZE[0]:
                right = False
            elif tail.direction is Direction.RIGHT and (index+1 < len(tails) and tails[index+1].direction is tail.direction) and tail.rect.topleft[0] == 0:
                left = False
            elif tail.direction is Direction.UP and tails[index-1].direction is tail.direction and tail.rect.topleft[1] == 0:
                top = False
            elif tail.direction is Direction.UP and (index+1 < len(tails) and tails[index+1].direction is tail.direction) and tail.rect.topleft[1] == settings.realsize[1]-TILE_SIZE[1]:
                bottom = False
            elif tail.direction is Direction.DOWN and tails[index-1].direction is tail.direction and tail.rect.topleft[1] == settings.realsize[1]-TILE_SIZE[1]:
                bottom = False
            elif tail.direction is Direction.DOWN and (index+1 < len(tails) and tails[index+1].direction is tail.direction) and tail.rect.topleft[1] == 0:
                top = False

        tail.make_surf(top, right, bottom, left)

    def add_tail(self, tail):
        self.tails.append(tail)

    def update_direction(self): # Funktioniert nicht im Wandlosspielmodus (braucht es auch nicht)
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
    def __init__(self, position: tuple, direction: Direction, size: tuple = (20, 20)):
        super(Tail, self).__init__()
        self.size = size
        self.surf = pygame.Surface(size)
        self.rect = self.surf.get_rect()
        self.rect.topleft = position

        self.direction = direction

    def update(self):
        # Bewegt sich
        if self.direction == Direction.UP:
            self.rect.move_ip(0, -self.size[1])
        elif self.direction == Direction.RIGHT:
            self.rect.move_ip(self.size[0], 0)
        elif self.direction == Direction.DOWN:
            self.rect.move_ip(0, self.size[1])
        elif self.direction == Direction.LEFT:
            self.rect.move_ip(-self.size[0], 0)

    def make_surf(self, top=True, right=True, bottom=True, left=True):
        """Erstellt die Textur"""
        self.surf.fill(MAINCOLOR)
        if top:
            pygame.draw.line(self.surf, EDGECOLOR, (0, 0), (TILE_SIZE[0]-1, 0)) # oben entlang
        if right:
            pygame.draw.line(self.surf, EDGECOLOR, (TILE_SIZE[0]-1, 0), (TILE_SIZE[0]-1, TILE_SIZE[1]-1)) # rechts entlang
        if bottom:
            pygame.draw.line(self.surf, EDGECOLOR, (0, TILE_SIZE[0]-1), (TILE_SIZE[0]-1, TILE_SIZE[1]-1)) # untem entlang
        if left:
            pygame.draw.line(self.surf, EDGECOLOR, (0, 0), (0, TILE_SIZE[1]-1)) # links entlang
        self.edges = {"top": top, "right": right, "bottom": bottom, "left": left}
