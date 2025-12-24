# bullet.py
import pygame
from settings import TILE, BULLET_COLOR, BULLET_SPEED, COLS, ROWS
import assets

class Bullet:
    def __init__(self, cell_x, cell_y, direction, is_enemy=False):
        
        self.x = float(cell_x)
        self.y = float(cell_y)
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

        # вийшла за межі поля
        if self.x < 0 or self.x >= COLS or self.y < 0 or self.y >= ROWS:
            self.active = False
            return

        # колізія з блоками
        cell_x = int(self.x)
        cell_y = int(self.y)
        if level.hit_cell(cell_x, cell_y):
            self.active = False

        if self.is_enemy:
            px, py = player.get_grid_pos()
            if int(self.x) == px and int(self.y) == py:
                did_damage = player.take_damage()
                self.active = False
                return did_damage
    
    def check_base_collision(self, base):
        if not self.active:
            return False
            
        # Тільки ворожі кулі можуть знищити базу
        if not self.is_enemy:
            return False
            
        # Перевірка координат 
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
        cx = int(self.x * TILE + TILE / 2)
        cy = int(self.y * TILE + TILE / 2)
        pygame.draw.circle(screen, BULLET_COLOR, (cx, cy), TILE // 6)

        if self.direction == "UP":
            img = assets.bullet
        elif self.direction == "DOWN":
            img = assets.bullet
        elif self.direction == "LEFT":
            img = assets.bullet_hor
        else:  # RIGHT
            img = assets.bullet_hor

        if img is None:
            return

        px = self.x * TILE
        py = self.y * TILE
        screen.blit(img, (px, py))
