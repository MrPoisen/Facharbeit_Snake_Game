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
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

        # Spiel/Spielstand
        self.clock = pygame.time.Clock()
        self.running = False
        self.quit = False

        # Spieler
        self.snake = SnakeHead()
        self.apple = Apple(get_apple_position(self.snake, self.settings.size))

        # Spielobjekte
        self.all_entities = pygame.sprite.Group(self.apple, self.snake)
        self.tails = pygame.sprite.Group()

        # Spielobjekte mit der Snake "verbinden"
        self.snake.tail_group = self.tails
        self.snake.all_group = self.all_entities

        self.mainscreen = resize(self.settings.size)

    def events(self):
        for event in pygame.event.get():

            if event.type == KEYDOWN:
                if event.key == K_BACKSPACE:  # Spiel beenden
                    self.running = False

                if event.key == K_ESCAPE:
                    self.pause()

            elif event.type == QUIT:
                self.running = False
                self.quit = True
                #pygame.quit()

    def apple_logic(self):
        collide_with_apple = False
        if pygame.sprite.collide_rect(self.snake.next_pos(), self.apple):
            collide_with_apple = True
            apple_position = get_apple_position(self.snake, self.settings.size, self.apple.rect.topleft)
            self.apple.kill()  # Entfernt den Apfel von 'all_entities'
            if apple_position is False:
                # Spiel ist zu ende, der Spieler hat gewonnen
                self.running = False
                self.win()
            self.apple = Apple(apple_position)
            self.all_entities.add(self.apple)

        self.snake.update(collide_with_apple)  # Bewegt den Spieler

    def snake_logic(self):
        if hits_wall(self.snake, self.settings.size) or pygame.sprite.spritecollide(self.snake, self.tails, dokill=False):
            # Wenn die Snake gegen eine Wand oder gegen ein Schwanzteil trifft
            self.running = False
            self.dead()

    def blit_background(self):
        for i in range(self.settings.size[0]//TILE_SIZE[0]):
            for ii in range(self.settings.size[1]//TILE_SIZE[1]):
                if (i % 2 == 0 and ii % 2 == 0) or (i % 2 != 0 and ii % 2 != 0):
                    pygame.draw.rect(self.mainscreen, (30, 30, 30, 100),  # Farbe ist ein dunkles Grau
                                     pygame.Rect(i*TILE_SIZE[0], ii*TILE_SIZE[1], *TILE_SIZE))
                else:
                    pygame.draw.rect(self.mainscreen, THECOLORS.get("black"),
                                     pygame.Rect(i * TILE_SIZE[0], ii * TILE_SIZE[1], *TILE_SIZE))

    def run(self) -> None:
        self.running = True
        passed_time = 0  # time till next move

        self.blit_background()
        for entity in self.all_entities:
            self.mainscreen.blit(entity.surf, entity.rect)
        pygame.display.flip()

        while self.running:
            dt = self.clock.tick(self.settings.fps)
            passed_time += dt

            self.events()

            # Die Richtung, in die sich die Schlange bewegen soll, kann jederzeit geändert werden
            self.snake.accept_direction(pygame.key.get_pressed())

            if passed_time >= (1000/self.settings.snakespeed):
                # Wenn die vergangene Zeit größer ist als 1000 durch Wie oft die Schlange sich pro sekunde Bewegen soll
                # durch '1000/' werden die Sekunden der snakespeed in millisekunden umgerechnet
                passed_time = 0
                self.apple_logic()
                self.snake_logic()

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
                    wait = False
                    self.running = False
                    self.quit = True

    def dead(self):
        wait = True
        # texts
        pause_text1 = FONT.render(f'Du hast {len(self.snake.tails)} Punkte erreicht', False, THECOLORS.get("white"))
        pause_text2 = FONT.render('Drücke ESC um fortzufahren', False, THECOLORS.get("white"))

        grey_surf = pygame.Surface(self.settings.size)
        grey_surf.fill((20, 20, 20, 180))
        grey_surf.set_alpha(180)
        self.mainscreen.blit(grey_surf, grey_surf.get_rect())

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
                    wait = False
                    self.running = False
                    self.quit = True

    def win(self):
        wait = True
        # texts
        pause_text1 = FONT.render(f'Du hast gewonnen!', False, THECOLORS.get("white"))
        pause_text2 = FONT.render('Drücke ESC um fortzufahren', False, THECOLORS.get("white"))

        grey_surf = pygame.Surface(self.settings.size)
        grey_surf.fill((20, 20, 20, 180))
        grey_surf.set_alpha(180)
        self.mainscreen.blit(grey_surf, grey_surf.get_rect())

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
                    wait = False
                    self.running = False
                    self.quit = True

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

        self.snake.update(collide_with_apple, False)
        if collide_with_apple:
            tail_to_switch = self.snake.tails.pop()
            self.snake.rect, tail_to_switch.rect = tail_to_switch.rect, self.snake.rect  # Positionen werden getauscht
            self.snake.tails.reverse()  # Sollte so funktionieren
            self.snake.tails.append(tail_to_switch)

            self.snake.update_direction()  # Richtung der Schlange wird angepasst
        self.snake.texture()

class WithoutWall(Game):
    def snake_logic(self):
        self.move(self.snake)
        for tail in self.snake.tails:
            self.move(tail)

        self.snake.texture(self.settings)
        if pygame.sprite.spritecollide(self.snake, self.tails, dokill=False):
            # Wenn die Snake gegen eine Wand trifft oder gegen ein Schwanzteil
            self.running = False
            self.dead()

    def apple_logic(self):
        collide_with_apple = False
        sprite = self.snake.next_pos()
        self.move(sprite)
        if pygame.sprite.collide_rect(sprite, self.apple):
            collide_with_apple = True
            apple_position = get_apple_position(self.snake, self.settings.size, self.apple.rect.topleft)
            self.apple.kill()  # Entfernt den Apfel von 'all_entities'
            if apple_position is False:
                # Spiel ist zu ende, der Spieler hat gewonnen
                self.running = False
                self.win()
            self.apple = Apple(apple_position)
            self.all_entities.add(self.apple)

        self.snake.update(collide_with_apple, False)  # Bewegt den Spieler

    def move(self, obj):
        topleft = obj.rect.topleft
        if topleft[0] < 0:
            obj.rect.topleft = (self.settings.size[0]-TILE_SIZE[0], topleft[1])
        elif topleft[0] >= self.settings.size[0]:
            obj.rect.topleft = (0, topleft[1])
        elif topleft[1] < 0:
            obj.rect.topleft = (topleft[0], self.settings.size[1]-TILE_SIZE[1])
        elif topleft[1] >= self.settings.size[1]:
            obj.rect.topleft = (topleft[0], 0)

def get_apple_position(snake: SnakeHead, size: Tuple[int, int], old_apple_topleft=None) -> Union[tuple, bool]:
    """
    Die Funktion gibt eine zufällige, freie Position für den Apfel zurück.
    Das Argument 'old_apple_topleft' wird genutzt, damit der Apfel nicht erneut an derselben Stelle auftaucht
    """
    # Hier werden alle bereits Verwendeten Positionen in einem Set gespeichert
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
    if len(possible_positions) == 0:
        return False
    
    return random.choice(possible_positions)

def run(settings: Settings, presize: Tuple[int, int]) -> Tuple[pygame.Surface, bool]:
    GAMEMODES = {"default": Game, "no_walls": WithoutWall, "switching_head": HeadSwitch}
    game_class = GAMEMODES.get(settings.gamemode)
    game = game_class(settings)
    game.run()
    screen = resize(presize)
    return screen, game.quit
