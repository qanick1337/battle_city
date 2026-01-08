# level_builder.py
import pygame
import random

import os

from settings import TILE, COLS, ROWS, GRASS, STEEL, BRICK, WATER, EMPTY
import assets

# 1- цегла, 2-сталь, 3-вода, 4-трава
# # - цегла, @ - сталь, ~ - вода, % - трава, . - нічого

class Level:
    def __init__(self):
        self.enemy_spawn_points = [
            (2, 1),
            (COLS // 2, 1),
            (COLS - 3, 1),
        ]

        self.grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]
        self.create_border()
        self.generate_valid_level() 

    def create_border(self):
        for x in range(COLS):
            self.grid[0][x] = STEEL
            self.grid[ROWS - 1][x] = STEEL
        for y in range(ROWS):
            self.grid[y][0] = STEEL
            self.grid[y][COLS - 1] = STEEL

    def reset_grid(self):
        self.grid = [[EMPTY for x in range(COLS)] for y in range(ROWS)]
        self.create_border()

    def generate_random_level(self):
        for y in range(2, ROWS - 2, 2):
            for x in range(2, COLS // 2, 2):

                r = random.random()
                
                if r < 0.15:
                    self.grid[y][x] = WATER

                elif r < 0.25:
                    self.grid[y][x] = STEEL
                    if x + 1 < COLS - 1:
                        self.grid[y][x + 1] = STEEL

                elif r < 0.50:
                    height = random.randint(2, 5)
                    self.add_vertical_line(x, y, height, BRICK)

                elif r < 0.75:
                    width = random.randint(2, 5)
                    self.add_horizontal_line(x, y, width, BRICK)

                else:
                    self.grid[y][x] = GRASS
                    if x + 1 < COLS - 1 and random.random() < 0.5:
                        self.grid[y][x + 1] = GRASS

        for y in range(ROWS):
            for x in range(COLS // 2):
                self.grid[y][COLS - 1 - x] = self.grid[y][x]

        for spawn_x, spawn_y in self.enemy_spawn_points:
            if 0 <= spawn_x < COLS and 0 <= spawn_y < ROWS:
                self.grid[spawn_y][spawn_x] = EMPTY

    def add_vertical_line(self, x, y, length, type_id):
        for i in range(length):
            if y + i < ROWS - 1:
                self.grid[y + i][x] = type_id

    def add_horizontal_line(self, x, y, length, type_id):
        for i in range(length):
            if x + i < COLS - 1:
                self.grid[y][x + i] = type_id

    def tile_is_walkable(self, x, y):
        return self.grid[y][x] in (EMPTY, GRASS)

    def bfs(self, spawn_x, spawn_y):
        if not self.tile_is_walkable(spawn_x, spawn_y):
            return set()

        visited_tiles = set([(spawn_x, spawn_y)])
        queue = [(spawn_x, spawn_y)]

        while len(queue) != 0:
            (x, y) = queue.pop(0)
            for (dx, dy) in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                (new_x, new_y) = (x + dx, y + dy)
                if 0 <= new_x < COLS and 0 <= new_y < ROWS:
                    if (new_x, new_y) not in visited_tiles and self.tile_is_walkable(new_x, new_y):
                        visited_tiles.add((new_x, new_y))
                        queue.append((new_x, new_y))

        return visited_tiles

    def is_level_valid(self):
        MIN_AREA = 45 
        MIN_EXIT_Y = 4

        for spawn_x, spawn_y in self.enemy_spawn_points:
            reachable_tiles = self.bfs(spawn_x, spawn_y)

            if len(reachable_tiles) < MIN_AREA:
                return False

            if not any(y >= MIN_EXIT_Y for (x, y) in reachable_tiles):
                return False

        return True

    def generate_valid_level(self, tries=999):
        for _try_ in range(tries):
            self.reset_grid()
            self.generate_random_level()
            if self.is_level_valid():
                return

    def can_move(self, new_x, new_y):
        if new_x < 0 or new_x >= COLS or new_y < 0 or new_y >= ROWS:
            return False
        tile = self.grid[new_y][new_x]
        return tile in (EMPTY, GRASS)

    def hit_cell(self, x, y):
        if 0 <= x < COLS and 0 <= y < ROWS:
            tile = self.grid[y][x]
            if tile == BRICK:
                self.grid[y][x] = EMPTY
                return True
            elif tile == STEEL:
                return True
        return False

    def load_from_file(self, filename):
        self.reset_grid()
        enemies = []

        with open(filename, 'r') as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]

        enemy_char_map = {
            'b': 'BASIC',
            'f': 'FAST',
            'a': 'ARMOR',
            's': 'SNIPER'
        }

        map_row = 0
        for line in lines:

            if line.startswith("ENEMIES:"):
                code_string = line.split(":")[1].strip()
                for char in code_string:
                    if char in enemy_char_map:
                        enemies.append(enemy_char_map[char])
                continue 

            if map_row < ROWS:
                for x in range(min(COLS, len(line))):
                    char = line[x]
                    if char == BRICK: self.grid[map_row][x] = BRICK
                    elif char == STEEL: self.grid[map_row][x] = STEEL
                    elif char == WATER: self.grid[map_row][x] = WATER
                    elif char == GRASS: self.grid[map_row][x] = GRASS
                    else: self.grid[map_row][x] = EMPTY
                
                map_row += 1

        for spawn_x, spawn_y in self.enemy_spawn_points:
             self.grid[spawn_y][spawn_x] = EMPTY
             
        if not enemies:
            enemies = ["BASIC"] * 20 

        return enemies

    def draw(self, screen):
        for row in range(ROWS):
            for col in range(COLS):
                tile = self.grid[row][col]
                px = col * TILE
                py = row * TILE

                if tile == BRICK:
                    screen.blit(assets.brick, (px, py))
                elif tile == STEEL:
                    screen.blit(assets.steel, (px, py))
                elif tile == WATER:
                    screen.blit(assets.water, (px, py))

    def draw_grass(self, screen):
        for row in range(ROWS):
            for col in range(COLS):
                if self.grid[row][col] == GRASS:
                    px = col * TILE
                    py = row * TILE
                    screen.blit(assets.grass, (px, py))
