# assets.py
import os
import pygame
from settings import TILE

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")

player_up = None
player_down = None
player_left = None
player_right = None

enemy_up = None
enemy_down = None
enemy_left = None
enemy_right = None

brick = None
steel = None
water = None
grass = None

bullet_vertical = None
bullet_horizontal = None
explossion = None

bonus_images = None
base = None
base_destroyed = None

def load_image(filename, size):
    path = os.path.join(ASSETS_DIR, filename)
    image = pygame.image.load(path)
    if pygame.display.get_surface():
        image = image.convert_alpha()
    return pygame.transform.scale(image, (size, size))


def load_assets():
    global player_up, player_down, player_left, player_right, enemy_up, enemy_down, enemy_left, enemy_right, brick, steel, water, bullet_vertical, bullet_horizontal, grass, explossion, bonus_images, base, base_destroyed

    player_up = load_image("tank_top.png", TILE)
    player_down = load_image("tank_bottom.png", TILE)
    player_left = load_image("tank_left.png", TILE)
    player_right = load_image("tank_right.png", TILE)
 
    enemy_up = load_image("enemy_top.png", TILE)
    enemy_down = load_image("enemy_bottom.png", TILE)
    enemy_left = load_image("enemy_left.png", TILE)
    enemy_right = load_image("enemy_right.png", TILE)

    brick = load_image("brick.webp", TILE)
    steel = load_image("steel.webp", TILE)
    water = load_image("water.jpg", TILE)
    grass = load_image("leaves.webp", TILE)

    bullet_vertical = load_image("bullet.png",TILE)
    bullet_horizontal = load_image("bullet _hor.png", TILE)
    explossion = load_image("explossion_tank.png", TILE)

    bonus_images = {
        "GRENADE": load_image("grenade.png", TILE),
        "SHIELD": load_image("shield.png", TILE),
        "HEART": load_image("heart.png", TILE),
        "FREEZE": load_image("freeze.png", TILE),
        "SHOVEL": load_image("showel.png", TILE)
    }

    base = load_image("base.png", TILE)
    base_destroyed = load_image("base_destroyed.png", TILE)
