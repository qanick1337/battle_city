from settings import TILE, FPS
import assets

class Bonus:
    def __init__(self, x, y, bonus_type):
        self.x = x  # координата в клітинках
        self.y = y
        self.type = bonus_type # "STAR", "GRENADE", "HELMET" тощо
        self.timer = FPS * 10 # бонус зникає через 10 секунд, якщо не підібрати
        self.image = assets.bonus_images[bonus_type]

    def draw(self, screen):
        screen.blit(self.image, (self.x * TILE, self.y * TILE))