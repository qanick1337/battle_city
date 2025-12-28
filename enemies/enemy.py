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
        
        # Завантажуємо характеристики з "конфіга"
        stats = ENEMY_TYPES.get(enemy_type, ENEMY_TYPES["BASIC"])
        
        self.speed_delay = stats["speed"]
        self.hp = stats["hp"]
        self.hue = stats.get("hue", None)
        self.score = stats["score"]
        
        # Налаштування стрільби
        shoot_range = stats.get("shoot_freq", (60, 180)) # (min, max)
        self.shoot_min, self.shoot_max = shoot_range

        self.direction = "DOWN"
        
        # Лічильники
        self.move_timer = self.speed_delay
        self.shoot_timer = random.randint(self.shoot_min, self.shoot_max)

        self.alive = True

        self.sprites = self.get_sprites_for_type(enemy_type, self.hue)

    @property
    def rect(self):
        return pygame.Rect(self.x * TILE, self.y * TILE, TILE, TILE)

    @classmethod
    def get_sprites_for_type(cls, enemy_type, hue):
        """
        Розумне кешування. Перевіряє, чи генерували ми вже картинки 
        для цього типу ворогів. Якщо ні - генерує і зберігає.
        """
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
        """
        Змінює Hue (відтінок) картинки, зберігаючи яскравість і прозорість.
        Працює повільно, тому результат ТРЕБА кешувати.
        """
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
        
        # Мерехтіння для ARMOR танків
        self.invincible = 10
        return False

    def update(self, level, bullets, player):
        if self.invincible > 0:
            self.invincible -= 1

        if not self.alive:
            return

        self.check_line_of_sight(player, bullets)

        # Звичайна стрільба за таймером
        self.shoot_timer -= 1
        if self.shoot_timer <= 0:
            self.shoot(bullets)
            self.shoot_timer = random.randint(self.shoot_min, self.shoot_max)

        # Рух
        if self.move_timer > 0:
            self.move_timer -= 1
            return
        
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
            # якщо врізався → змінюємо напрямок
            self.change_direction_smart(level, player)   

    def check_line_of_sight(self, player, bullets):

        if self.type == "SNIPER":
            reaction_chance = 0.7
        else:
            reaction_chance = 0.3
        
        if random.random() > reaction_chance:
            return

        player_x, player_y = player.get_grid_pos()
        
        # Перевірка по вертикалі (X співпадає)
        if self.x == player_x:
            dist = abs(self.y - player_y)
            if dist < 6: 

                # Рахуємо, в якому напрямку нам рухатися, щоб наздогнати гравця
                if player_y < self.y:
                    needed_dir = "UP"
                else: 
                    needed_dir =  "DOWN"    
                
                # Якщо ми не дивимось на нього - повертаємось
                if self.direction != needed_dir:
                    self.direction = needed_dir
                    self.move_timer = 30
                    self.shoot_timer = 50
                
                # Стріляємо миттєво, якщо вистріл не був зроблений 1/3 секунди тому
                if self.shoot_timer <= 20: 
                    self.shoot(bullets)
                    self.shoot_timer = random.randint(self.shoot_min, self.shoot_max)

        # Перевірка по горизонталі (Y співпадає)
        elif self.y == player_y:
            dist = abs(self.x - player_x)
            if dist < 6:
                if player_x < self.x:
                    needed_dir = "LEFT"
                else: 
                    needed_dir =  "RIGHT"
                
                if self.direction != needed_dir:
                    self.direction = needed_dir
                    self.move_timer = 30
                    self.shoot_timer = 50
                
                if self.shoot_timer <= 20: # Якщо не щойно стріляли
                    self.shoot(bullets)
                    self.shoot_timer = random.randint(self.shoot_min, self.shoot_max)

    def change_direction_smart(self, level, player):
        options = []
        
        directions = [
            ("UP", 0, -1, 5),
            ("DOWN", 0, 1, 20),
            ("LEFT", -1, 0, 15),
            ("RIGHT", 1, 0, 15)
        ]
        
        player_x, player_y = player.get_grid_pos()

        dist_x = abs(player_x - self.x)
        dist_y = abs(player_y - self.y)

        is_tracking_active = dist_y > 3 and dist_x >3

        for direction, dx, dy, weight in directions:
            nx, ny = self.x + dx, self.y + dy
            
            if not level.can_move(nx, ny):
                continue
            
            # 2. Модифікатор: Якщо це напрямок до гравця - збільшуємо вагу
            if is_tracking_active:
                if direction == "DOWN" and player_y > self.y: 
                    weight += 30
                if direction == "UP" and player_y < self.y: 
                    weight += 20
                if direction == "LEFT" and player_x < self.x: 
                    weight += 30
                if direction == "RIGHT" and player_x > self.x: 
                    weight += 30
            
            # Додаємо цей напрямок у список стільки разів, яка його вага
            options.append(direction)

            for num in range(weight):
                options.append(direction)

        # Момент вибору напрямку
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
