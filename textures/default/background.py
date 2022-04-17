import pygame

def drawexample(texturepack):
    surface = pygame.Surface(texturepack._settings.realsize)
    for i in range(texturepack._settings.size[0]): # x-Achse
        for ii in range(texturepack._settings.size[1]): # y-Achse
            rect = pygame.Rect(i * texturepack._settings.tilesize[0], ii * texturepack._settings.tilesize[1], *texturepack._settings.tilesize)
            if (i % 2 == 0 and ii % 2 == 0) or (i % 2 != 0 and ii % 2 != 0):
                pygame.draw.rect(surface, (30, 30, 30, 100),  # Farbe ist ein dunkles Grau
                                 rect)
            else:
                pygame.draw.rect(surface, (190, 190, 40, 100),
                                 rect)
    return surface
