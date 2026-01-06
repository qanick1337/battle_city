# level_builder.py
import pygame
import random
from collections import deque

import os

from settings import TILE, COLS, ROWS
import assets

# 1- цегла, 2-сталь, 3-вода, 4-трава

class Level:
    def __init__(self):
        self.enemy_spawn_points = [
            (2, 1),
            (COLS // 2, 1),
            (COLS - 3, 1),
        ]

        self.grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]
        self.create_border()
        self.generate_valid_level(tries=200)  # <-- варіант B

    def create_border(self):
        for x in range(COLS):
            self.grid[0][x] = 2
            self.grid[ROWS - 1][x] = 2
        for y in range(ROWS):
            self.grid[y][0] = 2
            self.grid[y][COLS - 1] = 2

    def reset_grid_keep_border(self):
        self.grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]
        self.create_border()

    def generate_random_level(self):
        # 1) Генерація перешкод (ліва половина)
        for y in range(2, ROWS - 2, 2):
            for x in range(2, COLS // 2, 2):

                r = random.random()
                
                # 1. Вода (Шанс 15%: від 0.0 до 0.15)
                if r < 0.15:
                    self.grid[y][x] = 3

                # 2. Сталь (Шанс 10%: від 0.15 до 0.25)
                elif r < 0.25:
                    self.grid[y][x] = 2
                    if x + 1 < COLS - 1:
                        self.grid[y][x + 1] = 2

                # 3. Вертикальна стіна (Шанс 25%: від 0.25 до 0.50)
                elif r < 0.50:
                    height = random.randint(2, 5)
                    self.add_vertical_line(x, y, height, 1)

                # 4. Горизонтальна стіна (Шанс 25%: від 0.50 до 0.75)
                elif r < 0.75:
                    width = random.randint(2, 5)
                    self.add_horizontal_line(x, y, width, 1)

                # 5. Трава (Шанс 25%: від 0.75 до 1.0)
                else:
                    self.grid[y][x] = 4
                    if x + 1 < COLS - 1 and random.random() < 0.5:
                        self.grid[y][x + 1] = 4

        # 2) Віддзеркалення (Mirroring) правої частини
        for y in range(ROWS):
            for x in range(COLS // 2):
                self.grid[y][COLS - 1 - x] = self.grid[y][x]

        # 3) Очистка зон спавну ворогів
        for sx, sy in self.enemy_spawn_points:
            if 0 <= sx < COLS and 0 <= sy < ROWS:
                self.grid[sy][sx] = 0

    def add_vertical_line(self, x, y, length, type_id):
        for i in range(length):
            if y + i < ROWS - 1:
                self.grid[y + i][x] = type_id

    def add_horizontal_line(self, x, y, length, type_id):
        for i in range(length):
            if x + i < COLS - 1:
                self.grid[y][x + i] = type_id

    # Валідація рівню
    def _is_walkable(self, x, y):
        return self.grid[y][x] in (0, 4)

    def bfs_from(self, spawn_x, spawn_y):
        if not (0 <= spawn_x < COLS and 0 <= spawn_y < ROWS):
            return set()
        if not self._is_walkable(spawn_x, spawn_y):
            return set()

        visited = set([(spawn_x, spawn_y)])
        q = deque([(spawn_x, spawn_y)])

        while q:
            x, y = q.popleft()
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < COLS and 0 <= ny < ROWS:
                    if (nx, ny) not in visited and self._is_walkable(nx, ny):
                        visited.add((nx, ny))
                        q.append((nx, ny))

        return visited

    def is_level_valid(self) -> bool:
        MIN_AREA = 45 
        MIN_EXIT_Y = 4

        for spawn_x, spawn_y in self.enemy_spawn_points:
            if self.grid[spawn_y][spawn_x] not in (0, 4):
                return False

            reachable = self.bfs_from(spawn_x, spawn_y)

            if len(reachable) < MIN_AREA:
                return False

            # є можливість реально піти вниз у гру
            if not any(y >= MIN_EXIT_Y for (x, y) in reachable):
                return False

        return True

    def generate_valid_level(self, tries=200):
        for _ in range(tries):
            self.reset_grid_keep_border()
            self.generate_random_level()
            if self.is_level_valid():
                return
        print("⚠️ Warning: could not generate a valid level, using last attempt.")

    # Фізичні взаємодії з блоками
    def can_move(self, nx, ny):
        if nx < 0 or nx >= COLS or ny < 0 or ny >= ROWS:
            return False
        tile = self.grid[ny][nx]
        return tile in (0, 4)

    def can_move_rect(self, rect: pygame.Rect) -> bool:
        left, top, w, h = rect
        right = left + w
        bottom = top + h
        max_x = COLS * TILE
        max_y = ROWS * TILE

        if left < 0 or top < 0 or right > max_x or bottom > max_y:
            return False

        col_start = int(left // TILE)
        col_end   = int((right - 1) // TILE)
        row_start = int(top // TILE)
        row_end   = int((bottom - 1) // TILE)

        for row in range(row_start, row_end + 1):
            for col in range(col_start, col_end + 1):
                tile = self.grid[row][col]
                if tile in (1, 2, 3):
                    return False
        return True

    def hit_cell(self, x, y):
        if 0 <= x < COLS and 0 <= y < ROWS:
            tile = self.grid[y][x]
            if tile == 1:
                self.grid[y][x] = 0
                return True
            elif tile == 2:
                return True
        return False

    def load_from_file(self, filename):
        self.reset_grid_keep_border()
        enemies = []

        with open(filename, 'r') as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]

        enemy_char_map = {
            'b': 'BASIC',
            'f': 'FAST',
            'a': 'ARMOR',
            's': 'SNIPER'
        }

        # Проходимо по рядках
        map_row = 0
        for line in lines:

            if line.startswith("ENEMIES:"):
                code_string = line.split(":")[1].strip()
                for char in code_string:
                    if char in enemy_char_map:
                        enemies.append(enemy_char_map[char])
                continue # Переходимо до наступного рядка, не малюємо це на карті

            if map_row < ROWS:
                for x in range(min(COLS, len(line))):
                    char = line[x]
                    if char == '#': self.grid[map_row][x] = 1
                    elif char == '@': self.grid[map_row][x] = 2
                    elif char == '~': self.grid[map_row][x] = 3
                    elif char == '%': self.grid[map_row][x] = 4
                    else: self.grid[map_row][x] = 0
                
                map_row += 1

        for spawn_x, spawn_y in self.enemy_spawn_points:
             self.grid[spawn_y][spawn_x] = 0
             
        if not enemies:
            enemies = ["BASIC"] * 20 

        return enemies

    def draw(self, screen):
        for row in range(ROWS):
            for col in range(COLS):
                tile = self.grid[row][col]
                px = col * TILE
                py = row * TILE

                if tile == 1:
                    screen.blit(assets.brick, (px, py))
                elif tile == 2:
                    screen.blit(assets.steel, (px, py))
                elif tile == 3:
                    screen.blit(assets.water, (px, py))

    def draw_grass(self, screen):
        for row in range(ROWS):
            for col in range(COLS):
                if self.grid[row][col] == 4:
                    px = col * TILE
                    py = row * TILE
                    screen.blit(assets.grass, (px, py))
