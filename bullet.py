# bullet.py
import pygame
from settings import TILE, BULLET_COLOR, BULLET_SPEED, COLS, ROWS
import assets

class Bullet:
    def __init__(self, cell_x, cell_y, direction, is_enemy=False):
        
        self.x = int(cell_x)
        self.y = int(cell_y)
        self.direction = direction
        self.is_enemy = is_enemy
        self.active = True

    def update(self, level, player):
        if not self.active:
            return

        if self.direction == "UP":
            self.y -= BULLET_SPEED
        elif self.direction == "DOWN":
            self.y += BULLET_SPEED
        elif self.direction == "LEFT":
            self.x -= BULLET_SPEED
        elif self.direction == "RIGHT":
            self.x += BULLET_SPEED

        if self.x < 0 or self.x >= COLS or self.y < 0 or self.y >= ROWS:
            self.active = False
            return

        if level.hit_cell(int(self.x), int(self.y)):
            self.active = False

        if self.is_enemy:
            player_x, player_y = player.get_grid_pos()
            if int(self.x) == player_x and int(self.y) == player_y:
                did_damage = player.take_damage()
                self.active = False
                return did_damage
    
    def check_base_collision(self, base):
        if not self.active:
            return False
            
        if not self.is_enemy:
            return False
            
        bullet_x = int(self.x)
        bullet_y = int(self.y)
        
        if bullet_x == base.x and bullet_y == base.y:
            base.destroy()
            self.active = False
            return True
            
        return False

    def draw(self, screen):
        if not self.active:
            return

        if self.direction in ("UP", "DOWN"):
            img = assets.bullet_vertical
        else:  
            img = assets.bullet_horizontal

        if img is None:
            return

        px = self.x * TILE
        py = self.y * TILE
        screen.blit(img, (px, py))
