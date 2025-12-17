# explosion.py
import pygame
from settings import TILE 
import assets

class Explosion:
    def __init__(self, cell_x, cell_y):
        self.x = cell_x
        self.y = cell_y

        self.frames = 20  # приблизно 2/6 секунди

    @property
    def rect(self):
        return pygame.Rect(self.x * TILE, self.y * TILE, TILE, TILE)

    def update(self):
        self.frames -= 1

    def draw(self, screen):
        screen.blit(assets.explossion, (self.x * TILE, self.y * TILE))

    @property
    def active(self):
        return self.frames > 0

