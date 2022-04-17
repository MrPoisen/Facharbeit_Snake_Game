# TexturePacks

Alle Subordner im Ordner 'textures' stellen Texturen für das Spiel da.
Sollte sich eine 'background.py' im Subordner befinden mit einer draw Funktion,
wird diese genutzt um den Hintergrund darzustellen.
Die draw Funktion sollte als erstes das TexturPack akzeptieren, gefolgt von einem Settings Objekt.

````Python
def draw(texturepack: TexturePack) -> pygame.Surface:
  surface = pygame.Surface(settings.realsize)
  for i in range(settings.size[0]): # x-Achse
      for ii in range(settings.size[1]): # y-Achse
          rect = pygame.Rect(i * texturepack._settings.tilesize[0], ii * texturepack._settingstilesize[1], *texturepack._settingstilesize)
          if (i % 2 == 0 and ii % 2 == 0) or (i % 2 != 0 and ii % 2 != 0):
            pygame.draw.rect(surface, (30, 30, 30, 100),  # Farbe ist ein dunkles Grau
                                   rect)
          else:
            pygame.draw.rect(surface, THECOLORS.get("black"),
                                   rect)
  return surface
````
