# base.py
import pygame
import assets
from settings import TILE

class Base:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.alive = True
        self.rect = pygame.Rect(x * TILE, y * TILE, TILE, TILE)

    def draw(self, screen):
        
        if self.alive:
            screen.blit(assets.base, (self.x * TILE, self.y * TILE))
        else:
            screen.blit(assets.base_destroyed, (self.x * TILE, self.y * TILE))


    def destroy(self):
        self.alive = False