# enemy.py
import pygame
import random
from settings import TILE, ENEMY_MOVE_DELAY
import assets

from bullet import Bullet

class Enemy:
    def __init__(self, cell_x, cell_y):
        # Координати у клітинках
        self.x = cell_x
        self.y = cell_y

        self.direction = random.choice(["UP", "DOWN", "LEFT", "RIGHT"])
        self.move_cooldown = ENEMY_MOVE_DELAY
        self.shoot_cooldown = random.randint(30, 90)

        self.size = TILE
        self.alive = True

    @property
    def rect(self):
        return pygame.Rect(self.x * TILE, self.y * TILE, TILE, TILE)

    def get_grid_pos(self):
        return self.x, self.y

    def update(self, level, bullets):
        if not self.alive:
            return

        # Стрільба
        self.shoot_cooldown -= 1
        if self.shoot_cooldown <= 0:
            self.shoot(bullets)
            self.shoot_cooldown = random.randint(60, 120)

        # Рух
        if self.move_cooldown > 0:
            self.move_cooldown -= 1
            return

        dx = dy = 0

        if self.direction == "UP":
            dy = -1
        elif self.direction == "DOWN":
            dy =  1
        elif self.direction == "LEFT":
            dx = -1
        elif self.direction == "RIGHT":
            dx =  1

        nx = self.x + dx
        ny = self.y + dy
    
        if level.can_move(nx, ny):
            self.x = nx
            self.y = ny
        else:
            # якщо врізався → змінюємо напрямок
            self.direction = random.choice(["UP", "DOWN", "LEFT", "RIGHT"])

        # затримка перед наступним кроком
        self.move_cooldown = ENEMY_MOVE_DELAY

    def shoot(self, bullets):
        cell_x, cell_y = self.get_grid_pos()
        bullet = Bullet(cell_x, cell_y, self.direction, is_enemy=True)
        bullets.append(bullet)

    def draw(self, screen):
        if self.direction == "UP":
            img = assets.enemy_up
        elif self.direction == "DOWN":
            img = assets.enemy_down
        elif self.direction == "LEFT":
            img = assets.enemy_left
        else:  # RIGHT
            img = assets.enemy_right

        if img is None:
            return

        enemy_x = self.x * TILE
        enemy_y = self.y * TILE
        screen.blit(img, (enemy_x, enemy_y))
