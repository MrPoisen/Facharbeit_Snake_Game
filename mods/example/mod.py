def add_paths():
    import sys, os
    directory = os.path.abspath(os.getcwd())
    mod_directory = os.path.abspath(os.path.join(directory, os.pardir))
    game_directory = os.path.abspath(os.path.join(mod_directory, os.pardir))
    sys.path.append(mod_directory)
    sys.path.append(game_directory)
add_paths()

from game import Game, get_apple_position
from gamemodes import Gamemode
import pygame
from sprites import Apple

class Increase(Game):
    def apple_logic(self):
        collide_with_apple = False
        if pygame.sprite.collide_rect(self.snake.next_pos(), self.apple): # Wenn der Spieler den Apfel isst
            collide_with_apple = True
            apple_position = get_apple_position(self.snake, self.settings, self.apple.rect.topleft)
            self.apple.kill()  # Entfernt den Apfel von 'all_entities'
            if apple_position is False:
                # Spiel ist zu ende, der Spieler hat gewonnen
                self.win()
                return
            self.apple = Apple(apple_position, self.texturepack)
            self.all_entities.add(self.apple)
            self.settings.snakespeed += 1

        self.snake.update(collide_with_apple)  # Bewegt den Spieler

#GAMEMODES = {"SPEED":Gamemode(Increase)}
