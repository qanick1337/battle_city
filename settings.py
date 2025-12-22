# settings.py
TILE = 40
COLS = 16
ROWS = 16
HUD_WIDTH = 250

WIDTH = COLS * TILE + HUD_WIDTH
HEIGHT = ROWS * TILE

BG_COLOR = 'black'
BULLET_COLOR = (255, 230, 80)
HUD_TEXT_COLOR = (255, 255, 255)
HUD_BG_COLOR = (20, 20, 20)

FPS = 60
BULLET_SPEED = 0.25
# BULLET_COLOR = (255, 230, 80)

PLAYER_SPEED_TILES = 15

ENEMY_MOVE_DELAY = PLAYER_SPEED_TILES*1.5  

ENEMY_TYPES = {
    "BASIC": {
        "speed": ENEMY_MOVE_DELAY, 
        "hp": 1, 
        "hue": None,
        "score": 100
    },
    "FAST": {
        "speed": ENEMY_MOVE_DELAY // 2, 
        "hue": 200, 
        "score": 200,
        "hp": 1
    },
    "ARMOR": {
        "speed": int(ENEMY_MOVE_DELAY * 1.5),
        "hp": 3, 
        "hue": 120, 
        "score": 400
    },
    "SNIPER": {
        "speed": ENEMY_MOVE_DELAY,
        "hp": 1,
        "hue": 0, 
        "score": 300,
        "shoot_freq": (30, 60) 
    }
}
TILE_TYPES = {
    0: {"name": "empty", "walkable": True,  "destructible": False, "stops_bullet": False},
    1: {"name": "brick", "walkable": False, "destructible": True,  "stops_bullet": True},
    2: {"name": "steel", "walkable": False, "destructible": False, "stops_bullet": True},
    3: {"name": "water", "walkable": False, "destructible": False, "stops_bullet": False}, # Кулі летять над водою
    4: {"name": "grass", "walkable": True,  "destructible": False, "stops_bullet": False},
}
