# enemy.py
import pygame
import random
from settings import TILE, ENEMY_TYPES
import assets

from bullet import Bullet

class Enemy:
    _sprite_cache = {}

    def __init__(self, cell_x, cell_y, enemy_type="BASIC"):
        self.x = cell_x
        self.y = cell_y
        self.type = enemy_type
        self.invincible = 0
        
        stats = ENEMY_TYPES.get(enemy_type, ENEMY_TYPES["BASIC"])
        
        self.speed_delay = stats["speed"]
        self.hp = stats["hp"]
        self.hue = stats.get("hue", None)
        self.score = stats["score"]
        
        shoot_range = stats.get("shoot_freq", (60, 180)) # (min, max)
        self.shoot_min, self.shoot_max = shoot_range

        self.direction = "DOWN"
        
        self.move_timer = self.speed_delay
        self.shoot_timer = random.randint(self.shoot_min, self.shoot_max)

        self.alive = True

        self.sprites = self.get_sprites_for_type(enemy_type, self.hue)

    @classmethod
    def get_sprites_for_type(cls, enemy_type, hue):
        # Ключ кешу, наприклад: "FAST_180" або "BASIC_None"
        cache_key = f"{enemy_type}_{hue}"
        
        if cache_key in cls._sprite_cache:
            return cls._sprite_cache[cache_key]

        # Якщо в кеші немає - генеруємо
        print(f"Generating sprites for {cache_key}...") # Для відладки
        
        original_sprites = {
            "UP": assets.enemy_up,
            "DOWN": assets.enemy_down,
            "LEFT": assets.enemy_left,
            "RIGHT": assets.enemy_right
        }
        
        generated = {}
        for direction, img in original_sprites.items():
            if img is None: continue
            
            if hue is not None:
                # Викликаємо функцію зміни HUE
                new_img = cls.colorize_surface(img, hue)
                generated[direction] = new_img
            else:
                generated[direction] = img
        
        # Зберігаємо в глобальний кеш класу
        cls._sprite_cache[cache_key] = generated
        return generated

    @staticmethod
    def colorize_surface(surface, target_hue):
        # Створюємо копію, щоб не псувати оригінал
        new_surface = surface.copy()
        
        # PixelArray дозволяє редагувати пікселі як 2D масив
        pixels = pygame.PixelArray(new_surface)
        
        # Проходимо по кожному пікселю (для 32x32 це швидко, ~1024 ітерації)
        for x in range(new_surface.get_width()):
            for y in range(new_surface.get_height()):
                # Отримуємо колір у форматі (r, g, b, a)
                raw_color = new_surface.unmap_rgb(pixels[x, y])
                
                # Якщо піксель повністю прозорий - пропускаємо
                if raw_color.a == 0:
                    continue
                
                # Конвертуємо в об'єкт pygame.Color для доступу до HSLA
                color = pygame.Color(raw_color.r, raw_color.g, raw_color.b, raw_color.a)
                
                # Отримуємо поточні (Hue, Saturation, Lightness, Alpha)
                h, s, l, a = color.hsla
                
                # Міняємо тільки Hue (від 0 до 360)
                # s (насиченість) і l (світлота) залишаються старими -> тіні зберігаються!
                color.hsla = (target_hue, s, l, a)
                
                # Записуємо назад
                pixels[x, y] = color
        
        # Обов'язково закриваємо PixelArray
        pixels.close()
        return new_surface

    def get_grid_pos(self):
        return self.x, self.y

    def take_damage(self):
        self.hp -= 1

        if self.hp <= 0:
            self.alive = False
            return True
        
        self.invincible = 10
        return False

    def update(self, level, bullets, player):
        if self.invincible > 0:
            self.invincible -= 1

        if not self.alive:
            return

        self.check_line_of_sight(player, bullets)

        self.shoot_timer -= 1

        if self.shoot_timer <= 0:
            self.shoot(bullets)
            self.shoot_timer = random.randint(self.shoot_min, self.shoot_max)

        # Якщо лічильник ще не закінчився - ворог не може рухатися
        if self.move_timer > 0:
            self.move_timer -= 1
            return
        
        # Рух ворога
        self.move_timer = self.speed_delay

        dx = dy = 0

        if self.direction == "UP":
            dy = -1
        elif self.direction == "DOWN":
            dy =  1
        elif self.direction == "LEFT":
            dx = -1
        elif self.direction == "RIGHT":
            dx =  1

        new_x = self.x + dx
        new_y = self.y + dy
    
        if level.can_move(new_x, new_y):
            self.x = new_x
            self.y = new_y
            if random.random() < 0.05:
                 self.change_direction_smart(level, player)
        else:
            # якщо врізався то змінюємо напрямок
            self.change_direction_smart(level, player)   

    def check_line_of_sight(self, player, bullets):
        if self.type == "SNIPER":
            reaction_chance = 0.7
        else:
            reaction_chance = 0.3
        
        if random.random() > reaction_chance:
            return

        player_x, player_y = player.get_grid_pos()
        
        needed_dir = None

        needed_dir_y = self.get_direction(self.x, player_x, self.y, player_y, "UP", "DOWN")
        needed_dir_x = self.get_direction(self.y, player_y, self.x, player_x, "LEFT", "RIGHT") 

        needed_dir = needed_dir_x or needed_dir_y

        if needed_dir and self.direction != needed_dir:
            self.direction = needed_dir
            self.move_timer = 30
            self.shoot_timer = 30

    def get_direction(self, coord_equal1, coord_equal2, coord_different1, coord_differen2, direction1, direction2):
        if coord_equal1 == coord_equal2:
            dist = abs(coord_different1-coord_differen2)
            if dist < 6:
                if coord_differen2 < coord_different1:
                    return direction1
                else:
                    return direction2
                

    def change_direction_smart(self, level, player):
        options = []
        
        directions = [
            ("UP", 0, -1, 5),
            ("DOWN", 0, 1, 20),
            ("LEFT", -1, 0, 15),
            ("RIGHT", 1, 0, 15)
        ]
        
        (player_x, player_y) = player.get_grid_pos()

        dist_x = abs(player_x - self.x)
        dist_y = abs(player_y - self.y)

        is_tracking_active = dist_y > 3 and dist_x >3

        for (direction, dx, dy, weight) in directions:
            new_x, new_y = self.x + dx, self.y + dy
            
            if not level.can_move(new_x, new_y):
                continue
            
            if is_tracking_active:
                if direction == "DOWN" and player_y > self.y: 
                    weight += 30
                if direction == "UP" and player_y < self.y: 
                    weight += 20
                if direction == "LEFT" and player_x < self.x: 
                    weight += 30
                if direction == "RIGHT" and player_x > self.x: 
                    weight += 30
            
            options.append(direction)

            for num in range(weight):
                options.append(direction)

        if options:
            self.direction = random.choice(options)
        else:
            self.direction = random.choice(["UP", "DOWN", "LEFT", "RIGHT"])

    def shoot(self, bullets):
        cell_x, cell_y = self.get_grid_pos()
        bullet = Bullet(cell_x, cell_y, self.direction, is_enemy=True)
        bullets.append(bullet)

    def draw(self, screen):
        img = self.sprites.get(self.direction)
        if img:
            if self.invincible > 0:
                return
            screen.blit(img, (self.x * TILE, self.y * TILE))
