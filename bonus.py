# bonus.py
from settings import TILE, FPS
import assets

class Bonus:
    def __init__(self, x, y, bonus_type):
        self.x = x 
        self.y = y
        self.type = bonus_type
        self.timer = FPS * 5 # бонус зникає через 5 секунд, якщо не підібрати 
        self.image = assets.bonus_images[bonus_type]

    def draw(self, screen):
        screen.blit(self.image, (self.x * TILE, self.y * TILE))