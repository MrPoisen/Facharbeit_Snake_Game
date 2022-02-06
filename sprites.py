import pygame
from pygame.color import THECOLORS
from pygame.locals import (
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
  )

from typing import List, Dict
from enum import Enum, auto


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
        #pygame.draw.circle(self.surf, THECOLORS.get("red"), (size[0]//2, size[1]//2), min((size[0]//2, size[1]//2)))
        self.rect = self.surf.get_rect()
        self.rect.topleft = position  # moves apple

class SnakeHead(pygame.sprite.Sprite):
    def __init__(self, size: tuple = (20, 20)):
        super(SnakeHead, self).__init__()
        self.surf = pygame.Surface(size)
        self.surf.fill(THECOLORS.get("green"))

        self.rect = self.surf.get_rect()
        self.direction = Direction.RIGHT
        self._lastdirection = self.direction
        self.tails: List[Tail] = []

        #
        self.tail_group = None
        self.all_group = None

    def next_pos(self, move_value: int = 20):
        move_x = 0
        move_y = 0
        if self.direction == Direction.RIGHT:
            move_x = move_value
        elif self.direction == Direction.LEFT:
            move_x = -move_value  # moves left
        elif self.direction == Direction.UP:
            move_y = -move_value
        elif self.direction == Direction.DOWN:
            move_y = move_value  # moves Down

        sprite = pygame.sprite.Sprite()
        sprite.rect = self.rect.move(move_x, move_y)
        return sprite

    def make_surf(self, top=True, right=True, bottom=True, left=True):
        self.surf.fill(THECOLORS.get("green"))
        if top:
            pygame.draw.line(self.surf, THECOLORS.get("darkgreen"), (0, 0), (20, 0))
        if right:
            pygame.draw.line(self.surf, THECOLORS.get("darkgreen"), (20, 0), (20, 20))
        if bottom:
            pygame.draw.line(self.surf, THECOLORS.get("darkgreen"), (0, 20), (20, 20))
        if left:
            pygame.draw.line(self.surf, THECOLORS.get("darkgreen"), (0, 0), (0, 20))

    def accept_direction(self, pressed_keys):
        if pressed_keys[K_UP] and self._lastdirection != Direction.DOWN:
            self.direction = Direction.UP
        if pressed_keys[K_DOWN] and self._lastdirection != Direction.UP:
            self.direction = Direction.DOWN
        if pressed_keys[K_LEFT] and self._lastdirection != Direction.RIGHT:
            self.direction = Direction.LEFT
        if pressed_keys[K_RIGHT] and self._lastdirection != Direction.LEFT:
            self.direction = Direction.RIGHT

    def update(self, collide_with_apple: bool = False, move_value: int = 20) -> None:
        self._lastdirection = self.direction  # verhindert illegale Bewegung
        old_topleft = self.rect.topleft

        next_pos_rect = self.next_pos(move_value).rect  # Bewegt 'rect'
        self.rect.update(next_pos_rect.left, next_pos_rect.top, self.rect.width, self.rect.height)

        if collide_with_apple:  # adds tail on the position the head was on before
            tail = Tail(old_topleft)
            #tail.outline(self.edgeblits)
            self.tails.insert(0, tail)
            self.tail_group.add(tail)
            self.all_group.add(tail)

        else:  # moves tails

            for index, tail in enumerate(self.tails):
                x = 0
                y = 0
                if old_topleft[0] == tail.rect.topleft[0]:  # topleft[0] = topleft.x
                    pass
                elif old_topleft[0] > tail.rect.topleft[0]:  # block before is more right
                    x = move_value
                else:
                    x = -move_value

                if old_topleft[1] == tail.rect.topleft[1]:
                    pass
                elif old_topleft[1] > tail.rect.topleft[1]:  # block before is more down
                    y = move_value
                else:
                    y = -move_value
                old_topleft = tail.rect.topleft

                tail.update(x, y)  # new topleft
        # Für die richtige Darstellung
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
        if len(self.tails) == 0:
            return
        # erster Schlangenteil
        if not len(self.tails) > 1:
            self.tails[0].make_surf(top, right, bottom, left)
            return
        if self.tails[0].rect.topleft[0] < self.tails[1].rect.topleft[0]:
            right = False
        elif self.tails[0].rect.topleft[0] > self.tails[1].rect.topleft[0]:
            left = False
        elif self.tails[0].rect.topleft[1] < self.tails[1].rect.topleft[1]:
            top = False
        elif self.tails[0].rect.topleft[1] < self.tails[1].rect.topleft[1]:
            bottom = False
        self.tails[0].make_surf(top, right, bottom, left)
        for index, tail in enumerate(self.tails[1:]):
            top = bottom = left = right = True
            if tail.rect.topleft[0] > self.tails[index - 1].rect.topleft[0]:
                right = False
            elif tail.rect.topleft[0] < self.tails[index - 1].rect.topleft[0]:
                left = False
            elif tail.rect.topleft[1] > self.tails[index - 1].rect.topleft[1]:
                top = False
            elif tail.rect.topleft[1] < self.tails[index - 1].rect.topleft[1]:
                bottom = False
            if index+1 < len(self.tails):
                if tail.rect.topleft[0] < self.tails[index+1].rect.topleft[0]:
                    right = False
                elif tail.rect.topleft[0] > self.tails[index+1].rect.topleft[0]:
                    left = False
                elif tail.rect.topleft[1] < self.tails[index+1].rect.topleft[1]:
                    top = False
                elif tail.rect.topleft[1] < self.tails[index+1].rect.topleft[1]:
                    bottom = False
            tail.make_surf(top, right, bottom, left)

    def add_tail(self, tail):
        self.tails.append(tail)

    def update_direction(self):
        snake_rect = self.rect
        next_taile_rect = self.tails[0].rect

        if snake_rect.x > next_taile_rect.x:
            self.direction = Direction.RIGHT
            self._lastdirection = Direction.invert(Direction.RIGHT)  # TODO: kann man auch direkt Direction.LEFT hinschreiben
        elif snake_rect.x < next_taile_rect.x:
            self.direction = Direction.LEFT
            self._lastdirection = Direction.invert(Direction.LEFT)
        elif snake_rect.y > next_taile_rect.y:
            self.direction = Direction.DOWN
            self._lastdirection = Direction.invert(Direction.UP)
        elif snake_rect.y < next_taile_rect.y:
            self.direction = Direction.UP
            self._lastdirection = Direction.invert(Direction.DOWN)

class Tail(pygame.sprite.Sprite):
    #outline = outline
    def __init__(self, position: tuple, size: tuple = (20, 20)):
        super(Tail, self).__init__()
        self.surf = pygame.Surface(size)
        self.surf.fill(THECOLORS.get("green"))
        self.rect = self.surf.get_rect()
        self.rect.topleft = position


    def update(self, x, y) -> None:
        self.rect.move_ip(x, y)
        #self.surf.blit(self.topsurf, (0, 0))

    def make_surf(self, top=True, right=True, bottom=True, left=True):
        self.surf.fill(THECOLORS.get("green"))
        if top:
            pygame.draw.line(self.surf, THECOLORS.get("darkgreen"), (0, 0), (20, 0))
        if right:
            pygame.draw.line(self.surf, THECOLORS.get("darkgreen"), (20, 0), (20, 20))
        if bottom:
            pygame.draw.line(self.surf, THECOLORS.get("darkgreen"), (0, 20), (20, 20))
        if left:
            pygame.draw.line(self.surf, THECOLORS.get("darkgreen"), (0, 0), (0, 20))
