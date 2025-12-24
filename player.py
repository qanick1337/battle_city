# player.py
import pygame
from settings import TILE, PLAYER_SPEED_TILES, ROWS
import assets


class Player:
    def __init__(self, cell_x, cell_y, lives = 3):

        self.start_pos = (cell_x, cell_y)

        self.x = cell_x
        self.y = cell_y
        self.direction = "UP"

        self.hp = 3
        self.invincible = 0

        self.lives = lives

        self.size = TILE
        self.move_cooldown = 0  # затримка між рухами

        self.spawn = (2, ROWS - 3)

        # Керування: група клавіш -> (direction, dx, dy)
        self.controls = {
            (pygame.K_w, pygame.K_UP):    lambda: ("UP",    0, -1),
            (pygame.K_s, pygame.K_DOWN):  lambda: ("DOWN",  0,  1),
            (pygame.K_a, pygame.K_LEFT):  lambda: ("LEFT", -1,  0),
            (pygame.K_d, pygame.K_RIGHT): lambda: ("RIGHT", 1,  0),
        }

    @property
    def rect(self):
        return pygame.Rect(self.x * TILE, self.y * TILE, TILE, TILE)

    def take_damage(self):
        if self.invincible > 0:
            return False
        
        self.hp -= 1

        if self.hp <= 0:
            self.lives -= 1
            return True
        
        return False

    def respawn(self):

        self.x, self.y = self.start_pos
        
        self.direction = "UP"
        self.hp = 1 

        self.invincible = 180 # 3 секунди невразливості 

    def handle_input(self, keys, level):
        if self.move_cooldown > 0:
            self.move_cooldown -= 1
            return

        # шукаємо першу натиснуту групу клавіш
        for key_group, action in self.controls.items():
            if any(keys[k] for k in key_group):
                direction, dx, dy = action()
                self.direction = direction

                new_x = self.x + dx
                new_y = self.y + dy

                if level.can_move(new_x, new_y):
                    self.x = new_x
                    self.y = new_y
                    self.move_cooldown = PLAYER_SPEED_TILES
                break

    def get_grid_pos(self):
        return self.x, self.y

    def update(self):
        if self.invincible > 0:
            self.invincible -= 1

    def draw(self, screen):
        img_by_dir = {
            "UP": assets.player_up,
            "DOWN": assets.player_down,
            "LEFT": assets.player_left,
            "RIGHT": assets.player_right,
        }
        img = img_by_dir.get(self.direction)

        if img is None:
            return
        
        if self.invincible > 0:
            сenter = (self.x * TILE + TILE // 2, self.y * TILE + TILE // 2)
            radius = TILE // 2 + 2
             # Малюємо тонке синє коло
            pygame.draw.circle(screen, (100, 100, 255), сenter, radius, width=2)

        screen.blit(img, (self.x * TILE, self.y * TILE))
