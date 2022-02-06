import pygame
from pygame.locals import (
    K_ESCAPE,
    KEYDOWN,
    QUIT,
    K_BACKSPACE
)
from pygame.color import THECOLORS

from typing import Union, Tuple
import random

from main import resize, center, TILE_SIZE
from sprites import SnakeHead, Apple, Tail
from settings import Settings

# TILE_SIZE = (20, 20)
pygame.font.init()
FONT = pygame.font.SysFont('Calibri', 30)

def hits_wall(obj: Union[SnakeHead, Tail], size: Tuple[int, int]):
    topleft = obj.rect.topleft

    if topleft[0] >= size[0] or topleft[1] >= size[1]:
        return True

    elif topleft[0] < 0 or topleft[1] < 0:
        return True

    return False

class Game:
    """
    Basisklasse für das Spiel, die bereits die standard Snake-Variante implementiert
    """
    def __init__(self, settings: Settings, screen) -> None:
        self.settings = settings

        # Spiel/Spielstand
        self.clock = pygame.time.Clock()
        self.running = False
        self.passed_frames = 0

        # Spieler
        self.snake = SnakeHead()
        self.apple = Apple(get_apple_position(self.snake, self.settings.size))

        # Spielobjekte
        self.all_entities = pygame.sprite.Group(self.apple, self.snake)
        self.tails = pygame.sprite.Group()

        # Spielobjekte mit der Snake "verbinden"
        self.snake.tail_group = self.tails
        self.snake.all_group = self.all_entities

        self.mainscreen = screen

    def events(self):
        for event in pygame.event.get():

            if event.type == KEYDOWN:
                if event.key == K_BACKSPACE:  # Spiel beenden
                    self.running = False

                if event.key == K_ESCAPE:
                    self.pause()

            elif event.type == QUIT:
                self.running = False
                pygame.quit()

    def apple_logic(self):
        collide_with_apple = False
        if pygame.sprite.collide_rect(self.snake.next_pos(), self.apple):
            collide_with_apple = True
            apple_position = get_apple_position(self.snake, self.settings.size, self.apple.rect.topleft)
            self.apple.kill()
            if apple_position is False:
                # Spiel ist zu ende, der Spieler hat gewonnen
                self.running = False
                self.win()
            self.apple = Apple(apple_position)
            self.all_entities.add(self.apple)

        self.snake.update(collide_with_apple)  # Bewegt den Spieler

    def snake_logic(self):
        if hits_wall(self.snake, self.settings.size) or pygame.sprite.spritecollide(self.snake, self.tails, dokill=False):
            # Wenn die Snake gegen eine Wand trifft oder gegen ein Schwanzteil
            self.running = False
            self.dead()

    def blit_background(self):
        for i in range(self.settings.size[0]//TILE_SIZE[0]):
            for ii in range(self.settings.size[1]//TILE_SIZE[1]):
                if (i % 2 == 0 and ii % 2 == 0) or (i % 2 != 0 and ii % 2 != 0):
                    pygame.draw.rect(self.mainscreen, (30, 30, 30, 100),
                                     pygame.Rect(i*TILE_SIZE[0], ii*TILE_SIZE[1], *TILE_SIZE))
                else:
                    pygame.draw.rect(self.mainscreen, THECOLORS.get("black"),
                                     pygame.Rect(i * TILE_SIZE[0], ii * TILE_SIZE[1], *TILE_SIZE))


    def run(self) -> None:
        #mainscreen = self.mainscreen

        self.running = True
        passed_frames = 0  # time till next move
        while self.running:
            dt = self.clock.tick(self.settings.fps)
            passed_frames += dt

            self.events()

            # Die Richtung, in die sich die Schlange bewegen soll, kann jederzeit geändert werden
            self.snake.accept_direction(pygame.key.get_pressed())

            if passed_frames >= (1000/self.settings.snakespeed):
                passed_frames = 0
                self.apple_logic()
                self.snake_logic()

            #self.mainscreen.fill(THECOLORS.get("black"))
            self.blit_background()

            for entity in self.all_entities:
                self.mainscreen.blit(entity.surf, entity.rect)

            pygame.display.flip()

    def pause(self):
        wait = True
        # texts
        pause_text1 = FONT.render('Pause', False, THECOLORS.get("white"))
        pause_text2 = FONT.render('Drücke ESC um fortzufahren', False, THECOLORS.get("white"))

        # text1
        pause_text1_centerpos = center(pause_text1, self.settings.size)
        self.mainscreen.blit(pause_text1, pause_text1_centerpos)

        # text2
        pause_text2_centerpos = center(pause_text2, self.settings.size)
        pause_text2_centerpos = (pause_text2_centerpos[0], pause_text2_centerpos[1] + pause_text2.get_height() + 20)  # 20: space beetween the texts
        self.mainscreen.blit(pause_text2, pause_text2_centerpos)

        pygame.display.flip()
        while wait:
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        wait = False

                    if event.key == K_BACKSPACE:
                        wait = False
                        self.running = False

                elif event.type == QUIT:
                    self.running = False
                    wait = False
                    pygame.quit()

    def dead(self):
        wait = True
        # texts
        pause_text1 = FONT.render('Du bist Tot', False, THECOLORS.get("white"))
        pause_text2 = FONT.render('Drücke ESC um fortzufahren', False, THECOLORS.get("white"))

        # text1
        pause_text1_centerpos = center(pause_text1, self.settings.size)
        self.mainscreen.blit(pause_text1, pause_text1_centerpos)

        # text2
        pause_text2_centerpos = center(pause_text2, self.settings.size)
        pause_text2_centerpos = (pause_text2_centerpos[0], pause_text2_centerpos[1] + pause_text2.get_height() + 20)  # 20: space beetween the texts
        self.mainscreen.blit(pause_text2, pause_text2_centerpos)

        pygame.display.flip()
        while wait:
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        wait = False

                    if event.key == K_BACKSPACE:
                        wait = False
                        self.running = False

                elif event.type == QUIT:
                    self.running = False
                    wait = False
                    pygame.quit()

    def win(self):
        pass

class HeadSwitch(Game):
    def apple_logic(self):
        collide_with_apple = False
        if pygame.sprite.collide_rect(self.snake.next_pos(), self.apple):
            collide_with_apple = True
            apple_position = get_apple_position(self.snake, self.settings.size, self.apple.rect.topleft)
            self.apple.kill()
            if apple_position is False:
                # Spiel ist zu ende, der Spieler hat gewonnen
                self.running = False
                self.win()
            self.apple = Apple(apple_position)
            self.all_entities.add(self.apple)

        self.snake.update(collide_with_apple)
        if collide_with_apple:
            tail_to_switch = self.snake.tails[-1]
            self.snake.rect, tail_to_switch.rect = tail_to_switch.rect, self.snake.rect  # Positionen werden getauscht
            self.snake.tails.reverse()  # Sollte so funktionieren

            self.snake.update_direction()  # Richtung der Schlange wird angepasst

class WithoutWall(Game):
    def snake_logic(self):
        if hits_wall(self.snake, self.settings.size):
            self.move(self.snake)
        for tail in self.snake.tails:
            self.move(tail)

        if pygame.sprite.spritecollide(self.snake, self.tails, dokill=False):
            # Wenn die Snake gegen eine Wand trifft oder gegen ein Schwanzteil
            self.running = False
            self.dead()

    def move(self, obj):
        topleft = obj.rect.topleft
        if topleft.x < 0:
            obj.rect.topleft = (self.settings.size[0]-TILE_SIZE[0], topleft.y)
        elif topleft.x >= self.settings.size[0]:
            obj.rect.topleft = (0, topleft.y)
        elif topleft.y < 0:
            obj.rect.topleft = (topleft.x, self.settings.size[1]-TILE_SIZE[1])
        elif topleft.y >= self.settings.size[1]:
            obj.rect.topleft = (topleft.x, 0)

def get_apple_position(snake: SnakeHead, size: Tuple[int, int], old_apple_topleft=None) -> Union[tuple, bool]:
    number_of_possible_positions = (size[0] // TILE_SIZE[0]) * (size[1] // TILE_SIZE[1])
    if 1 + len(snake.tails) >= number_of_possible_positions:
        return False

    # generate all possible positions
    used_positions = set()
    used_positions.add(snake.rect.topleft)  # use topleft as position
    if old_apple_topleft is not None: used_positions.add(old_apple_topleft)
    for tail in snake.tails:
        used_positions.add(tail.rect.topleft)


    possible_positions = []
    for topleft_x in range(0, size[0], TILE_SIZE[0]):
        for topleft_y in range(0, size[1], TILE_SIZE[1]):
            if (topleft_x, topleft_y) not in used_positions:
                possible_positions.append((topleft_x, topleft_y))

    return random.choice(possible_positions)

def run(settings: Settings, presize: Tuple[int, int]):
    GAMEMODES = {"default": Game, "no_walls": WithoutWall, "switching_head": HeadSwitch}
    game_class = GAMEMODES.get(settings.gamemode)
    screen = resize(settings.size)
    game_class(settings, screen).run()
    screen = resize(presize)
    return screen
