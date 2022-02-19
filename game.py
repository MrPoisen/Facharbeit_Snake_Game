import pygame
from pygame.locals import (
    K_ESCAPE,
    KEYDOWN,
    QUIT,
    K_BACKSPACE
) # Tastenevents
from pygame.color import THECOLORS

from typing import Union, Tuple
import random
import logging

# eigene Module
from main import resize, center, TILE_SIZE
from sprites import SnakeHead, Apple, Tail
from settings import Settings

pygame.font.init() # Aufrufen, falls pygame noch nicht initialisiert ist
FONT_NAME = 'Calibri'

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
    def __init__(self, settings: Settings, logger_file=None, lvl=10) -> None:
        self.settings = settings

        # Spiel/Spielstand
        self.clock = pygame.time.Clock()
        self.running = False
        self.quit = False

        # Spieler
        self.snake = SnakeHead(TILE_SIZE)
        self.snake.texture()
        self.apple = Apple(get_apple_position(self.snake, self.settings.realsize), TILE_SIZE)

        # Spielobjekte
        self.all_entities = pygame.sprite.Group(self.apple, self.snake)
        self.tails = pygame.sprite.Group()

        # Spielobjekte mit der Snake "verbinden"
        self.snake.tail_group = self.tails
        self.snake.all_group = self.all_entities

        self.mainscreen = resize(self.settings.realsize)

        # logging
        self.logger = None
        self.logger_file = logger_file
        self.logging = False if logger_file is None else True
        if self.logging:
            self.logger = logging.getLogger(__name__)
            self.logger.setLevel(lvl)
            format = logging.Formatter('%(name)s -> %(asctime)s : %(levelname)s : %(message)s', datefmt='%d/%m/%Y %H:%M:%S')
            fh = logging.FileHandler(logger_file)
            fh.setLevel(lvl)
            fh.setFormatter(format)
            self.logger.addHandler(fh)
            self.logger.info(f"instance of {type(self)} created")

    def events(self):
        for event in pygame.event.get():

            if event.type == KEYDOWN:
                if event.key == K_BACKSPACE:  # Spiel beenden und zum Hauptmenü
                    self.running = False

                if event.key == K_ESCAPE:
                    self.pause()

            elif event.type == QUIT:
                self.running = False
                self.quit = True

    def apple_logic(self):
        collide_with_apple = False
        if pygame.sprite.collide_rect(self.snake.next_pos(), self.apple):
            collide_with_apple = True
            apple_position = get_apple_position(self.snake, self.settings.realsize, self.apple.rect.topleft)
            self.apple.kill()  # Entfernt den Apfel von 'all_entities'
            if apple_position is False:
                # Spiel ist zu ende, der Spieler hat gewonnen
                self.running = False
                self.win()
                return
            self.apple = Apple(apple_position, TILE_SIZE)
            self.all_entities.add(self.apple)

        self.snake.update(collide_with_apple)  # Bewegt den Spieler

    def snake_logic(self):
        if hits_wall(self.snake, self.settings.realsize) or pygame.sprite.spritecollide(self.snake, self.tails, dokill=False):
            # Wenn die Snake gegen eine Wand oder gegen ein Schwanzteil trifft
            if self.logging:
                self.logger.debug(f"Collision with Wall: {hits_wall(self.snake, self.settings.realsize)}, Tails: {bool(pygame.sprite.spritecollide(self.snake, self.tails, dokill=False))}")
            self.running = False
            self.dead()

    def blit_background(self):
        for i in range(self.settings.realsize[0]//TILE_SIZE[0]): # x-Achse
            for ii in range(self.settings.realsize[1]//TILE_SIZE[1]): # y-Achse
                if (i % 2 == 0 and ii % 2 == 0) or (i % 2 != 0 and ii % 2 != 0):
                    pygame.draw.rect(self.mainscreen, (30, 30, 30, 100),  # Farbe ist ein dunkles Grau
                                     pygame.Rect(i*TILE_SIZE[0], ii*TILE_SIZE[1], *TILE_SIZE))
                else:
                    pygame.draw.rect(self.mainscreen, THECOLORS.get("black"),
                                     pygame.Rect(i * TILE_SIZE[0], ii * TILE_SIZE[1], *TILE_SIZE))

    def run(self) -> None:
        self.running = True
        passed_time = 0  # Zeit die seit der letzten Bildschirmaktualiserung vergangen ist

        self.blit_background()
        for entity in self.all_entities:
            self.mainscreen.blit(entity.surf, entity.rect)

        pygame.display.flip()

        while self.running:
            dt = self.clock.tick(self.settings.fps)
            passed_time += dt # passed_time und dt sind in ms

            self.events()

            # Die Richtung, in die sich die Schlange bewegen soll, kann jederzeit geändert werden
            self.snake.accept_direction(pygame.key.get_pressed())

            if passed_time >= (1000/self.settings.snakespeed):
                # Wenn die vergangene Zeit größer ist als 1000 durch 'Wie oft die Schlange sich pro sekunde Bewegen soll'
                # durch '1000/' werden die Sekunden der snakespeed in millisekunden umgerechnet
                # Beispiel: snakespeed = 2 (Schlange bewegt sich 2mal pro Sekunde) vergangene Zeit: 500ms | 500ms >=1000/2 -> 500ms >= 500 -> True
                self.apple_logic()
                self.snake_logic()

                self.blit_background()
                for entity in self.all_entities:
                    self.mainscreen.blit(entity.surf, entity.rect)

                pygame.display.flip()
                if self.logging:
                    self.logger.info(f"game updated after {passed_time}ms ({passed_time/1000}s")
                    self.logger.debug(f"Snake: Topleft: {self.snake.rect.topleft}, Direction: {self.snake.direction}, Edges: {self.snake.edges}")
                    for tail in self.snake.tails:
                        self.logger.debug(f"Tail: Topleft: {tail.rect.topleft}, Direction: {tail.direction}, Edges: {tail.edges}")

                passed_time = 0

        if self.logging:
            self.logger.info("game ended")

    def pause(self):
        if self.logging:
            self.logger.info("pause called")
        wait = True
        # texts
        size = int(self.settings.size[0] * 2.5)
        font = pygame.font.SysFont(FONT_NAME, size)
        pause_text1 = font.render('Pause', False, THECOLORS.get("white"))
        pause_text2 = font.render('Drücke ESC um fortzufahren', False, THECOLORS.get("white"))


        # text1
        pause_text1_centerpos = center(pause_text1, self.settings.realsize)
        self.mainscreen.blit(pause_text1, pause_text1_centerpos)

        # text2
        pause_text2_centerpos = center(pause_text2, self.settings.realsize)
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
                    wait = False
                    self.running = False
                    self.quit = True

    def dead(self):
        if self.logging:
            self.logger.info("dead called")
        wait = True
        # texts
        size = int(self.settings.size[0] * 2.5)
        font = pygame.font.SysFont(FONT_NAME, size)
        pause_text1 = font.render(f'Du hast {len(self.snake.tails)} Punkte erreicht', False, THECOLORS.get("white"))
        pause_text2 = font.render('Drücke ESC um fortzufahren', False, THECOLORS.get("white"))

        grey_surf = pygame.Surface(self.settings.realsize)
        grey_surf.fill((20, 20, 20, 180))
        grey_surf.set_alpha(180)
        self.mainscreen.blit(grey_surf, grey_surf.get_rect())

        # text1
        pause_text1_centerpos = center(pause_text1, self.settings.realsize)
        self.mainscreen.blit(pause_text1, pause_text1_centerpos)

        # text2
        pause_text2_centerpos = center(pause_text2, self.settings.realsize)
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
                    wait = False
                    self.running = False
                    self.quit = True

    def win(self):
        if self.logging:
            self.logger.info("win called")
        wait = True
        # texts
        size = int(self.settings.size[0] * 2.5)
        font = pygame.font.SysFont(FONT_NAME, size)
        pause_text1 = font.render(f'Du hast gewonnen!', False, THECOLORS.get("white"))
        pause_text2 = font.render('Drücke ESC um fortzufahren', False, THECOLORS.get("white"))

        grey_surf = pygame.Surface(self.settings.realsize)
        grey_surf.fill((20, 20, 20, 180))
        grey_surf.set_alpha(180)
        self.mainscreen.blit(grey_surf, grey_surf.get_rect())

        # text1
        pause_text1_centerpos = center(pause_text1, self.settings.realsize)
        self.mainscreen.blit(pause_text1, pause_text1_centerpos)

        # text2
        pause_text2_centerpos = center(pause_text2, self.settings.realsize)
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
                    wait = False
                    self.running = False
                    self.quit = True

class HeadSwitch(Game):
    def apple_logic(self):
        collide_with_apple = False
        if pygame.sprite.collide_rect(self.snake.next_pos(), self.apple):
            collide_with_apple = True
            apple_position = get_apple_position(self.snake, self.settings.realsize, self.apple.rect.topleft)
            self.apple.kill()
            if apple_position is False:
                # Spiel ist zu ende, der Spieler hat gewonnen
                self.running = False
                self.win()
                return
            self.apple = Apple(apple_position, TILE_SIZE)
            self.all_entities.add(self.apple)

        self.snake.update(collide_with_apple, False)
        if collide_with_apple:
            tail_to_switch = self.snake.tails.pop() # entfernt hinterstes Schwanzteil aus der Liste
            self.snake.rect, tail_to_switch.rect = tail_to_switch.rect, self.snake.rect  # Positionen werden getauscht
            self.snake.tails.reverse()  # Reihenfolge der Schwanzteile muss geändert werden
            self.snake.tails.append(tail_to_switch) # hinterstes Schwanzteil wird wieder angefügt

            self.snake.update_direction()  # Richtung der Schlange wird angepasst, falls nötig
        self.snake.texture(full=collide_with_apple) # Schlange wird Dargestellt

class WithoutWall(Game):
    def snake_logic(self):
        self.move(self.snake)
        for tail in self.snake.tails:
            self.move(tail)

        self.snake.texture(self.settings, self.collide_with_apple)
        if pygame.sprite.spritecollide(self.snake, self.tails, dokill=False):
            # Wenn die Snake gegen ein Schwanzteil trifft
            if self.logging:
                self.logger.debug(f"Collision with Tails")
            self.running = False
            self.dead()

    def apple_logic(self):
        self.collide_with_apple = False
        sprite = self.snake.next_pos()
        self.move(sprite)
        if pygame.sprite.collide_rect(sprite, self.apple):
            self.collide_with_apple = True
            apple_position = get_apple_position(self.snake, self.settings.realsize, self.apple.rect.topleft)
            self.apple.kill()  # Entfernt den Apfel von 'all_entities'
            if apple_position is False:
                # Spiel ist zu ende, der Spieler hat gewonnen
                self.running = False
                self.win()
                return
            self.apple = Apple(apple_position, TILE_SIZE)
            self.all_entities.add(self.apple)

        self.snake.update(self.collide_with_apple, False)  # Bewegt den Spieler


    def move(self, obj):
        topleft = obj.rect.topleft
        if topleft[0] < 0:
            obj.rect.topleft = (self.settings.realsize[0]-TILE_SIZE[0], topleft[1])
        elif topleft[0] >= self.settings.realsize[0]:
            obj.rect.topleft = (0, topleft[1])
        elif topleft[1] < 0:
            obj.rect.topleft = (topleft[0], self.settings.realsize[1]-TILE_SIZE[1])
        elif topleft[1] >= self.settings.realsize[1]:
            obj.rect.topleft = (topleft[0], 0)

def get_apple_position(snake: SnakeHead, size: Tuple[int, int], old_apple_topleft=None) -> Union[tuple, bool]:
    """
    Die Funktion gibt eine zufällige, freie Position für den Apfel zurück.
    Das Argument 'old_apple_topleft' wird genutzt, damit der Apfel nicht erneut an derselben Stelle auftaucht
    """
    # Hier werden alle bereits Verwendeten Positionen in einem Set gespeichert
    used_positions = set()
    used_positions.add(snake.rect.topleft)
    if old_apple_topleft is not None: used_positions.add(old_apple_topleft)
    for tail in snake.tails:
        used_positions.add(tail.rect.topleft)


    possible_positions = []
    for topleft_x in range(0, size[0], TILE_SIZE[0]): # Koordinaten auf der x-Achse
        for topleft_y in range(0, size[1], TILE_SIZE[1]): # Koordinaten auf der y-Achse
            if (topleft_x, topleft_y) not in used_positions:
                possible_positions.append((topleft_x, topleft_y))
    if len(possible_positions) == 0:
        return False

    return random.choice(possible_positions)

def run(settings: Settings, presize: Tuple[int, int], logger_file, lvl) -> Tuple[pygame.Surface, bool]:
    GAMEMODES = {"default": Game, "no_walls": WithoutWall, "switching_head": HeadSwitch}
    game_class = GAMEMODES.get(settings.gamemode)
    game = game_class(settings, logger_file, lvl)
    game.run()
    if game.quit:
        screen = game.mainscreen
    else:
        screen = resize(presize)
    return screen, game.quit
