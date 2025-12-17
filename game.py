import sys
import os
import random
import pygame
import assets

from enemy import Enemy
from settings import (
    WIDTH, HEIGHT, BG_COLOR, FPS, ROWS, COLS, HUD_WIDTH,
    HUD_TEXT_COLOR, TILE, HUD_BG_COLOR
)
from level_builder import Level
from player import Player
from bullet import Bullet
from explosion import Explosion


class Game:
    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Battle City: 1337 Edition")

        try:
            pygame.display.set_icon(pygame.image.load(os.path.join(assets.ASSETS_DIR, "tank.jpg")))
        except:
            pass

        assets.load_assets()

        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Consolas", 20)
        self.title_font = pygame.font.SysFont("Consolas", 40, bold=True)
        self.finish_font = pygame.font.SysFont("Consolas", 30)
        self.menu_font = pygame.font.SysFont("Consolas", 25)

        # Рівні складності
        self.difficulty_presets = {
            "EASY": {"player_hp":5, "max_enemies":5, "spawn_speed": FPS*4, "max_enemies_on_map":3},
            "NORMAL": {"player_hp": 3, "max_enemies": 10, "spawn_speed": FPS * 3, "max_enemies_on_map":5},
            "HARD":   {"player_hp": 1, "max_enemies": 20, "spawn_speed": FPS * 2, "max_enemies_on_map":10},
            "HARDCORE":   {"player_hp": 1, "max_enemies": 30, "spawn_speed": FPS * 1, "max_enemies_on_map":20}
        }

        # Поточні вибори в меню
        self.selected_difficulty = "NORMAL"
        self.game_mode = "ARCADE"
        self.campaign_level_num = 1

        # Стан гри: 'MENU', 'PLAY', 'GAME_OVER', 'WIN'
        self.state = "MENU"
        self.running = True

        # Константи геймплею
        self.MAX_ENEMIES_ON_SCREEN = None
        self.MAX_ENEMIES_PER_LEVEL = None
        self.ENEMY_SPAWN_INTERVAL = None
        self.DAMAGE_FLASH_DURATION = None

        # Створення ігрових об'єктів
        self.level = Level()
        self.player = None
        self.enemies = []
        self.bullets = []
        self.explosions = []


    def reset(self):
        # --- Ініціалізація світу ---
        self.player = Player((self.player.spawn))

        self.enemies = [
            Enemy(COLS // 2, 1),
            Enemy(COLS - 3, 1),
            Enemy(2, 1)
        ]

        self.bullets = []
        self.player_bullet = None

        self.enemy_counter = 0
        self.spawned_enemies = len(self.enemies)
        self.enemy_spawn_timer = self.ENEMY_SPAWN_INTERVAL

        self.explosions = []

        self.damage_flash_timer = 0

    # Головний цикл гри
    def run(self):
        while self.running:
            dt = self.clock.tick(FPS)

            if self.state == "MENU":
                self.handle_menu_events()
                self.draw_menu()

            elif self.state == "PLAY":
                self.handle_play_events()
                self.update_play()
                self.draw_play()

        pygame.quit()
        sys.exit()

    # Menu-events
    def handle_menu_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                # Вибір режиму за допомогою клавіш "A" та "C"
                if event.key == pygame.K_a:
                    self.game_mode = "ARCADE"
                    self.start_game()
                elif event.key == pygame.K_c:
                    self.game_mode = "CAMPAIGN"
                    self.campaign_level_num = 1 # Починаємо з першого
                    self.start_game()
                
                # Вибір складності
                elif event.key == pygame.K_1:
                    self.selected_difficulty = "EASY"
                elif event.key == pygame.K_2:
                    self.selected_difficulty = "NORMAL"
                elif event.key == pygame.K_3:
                    self.selected_difficulty = "HARD"
                elif event.key == pygame.K_4:
                    self.selected_difficulty = "HARDCORE"
                
                elif event.key == pygame.K_ESCAPE:
                    self.running = False     

    def draw_menu(self):
        self.screen.fill((20, 20, 20)) # Темний фон

        # Заголовок
        title = self.title_font.render("BATTLE CITY", True, (255, 215, 0))
        self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))

        # Вибір режиму
        self.draw_text_centered("Натисніть [A] для ARCADE Mode (Випадковий рівень)", 200, (255, 255, 255))
        self.draw_text_centered("Натисніть [C] для CAMPAIGN Mode (Проходження рівнів)", 240, (255, 255, 255))

        # Складність
        diff_text = f"Складність: < {self.selected_difficulty} >"
        if self.selected_difficulty == "HARDCORE":
            self.draw_text_centered(diff_text, 320, (255, 0, 0))
        else:
            self.draw_text_centered(diff_text, 320, (0, 255, 0))
        self.draw_text_centered("(Натисніть 1-Easy, 2-Normal, 3-Hard)", 350, (150, 150, 150))

        pygame.display.flip()

    def draw_text_centered(self, text, y, color):
        surf = self.menu_font.render(text, True, color)
        x = WIDTH // 2 - surf.get_width() // 2
        self.screen.blit(surf, (x, y))

    # Game-events
    def start_game(self):
        self.apply_difficulty_settings()

        if self.game_mode == "ARCADE":
            self.level.generate_valid_level()
        else:
            path = f"levels/level_{self.campaign_level_num}.txt"
            if not os.path.exists(path):
                print(f"Рівень {path} не знайдено! Генеруємо випадковий.")
                self.level.generate_valid_level()
            else:
                self.level.load_from_file(path) 

        self.reset_entities()
        self.state = "PLAY"

    def apply_difficulty_settings(self):
        settings = self.difficulty_presets[self.selected_difficulty]
        
        self.MAX_ENEMIES_ON_SCREEN = settings["max_enemies_on_map"]
        self.MAX_ENEMIES_PER_LEVEL = settings["max_enemies"]
        self.ENEMY_SPAWN_INTERVAL = settings["spawn_speed"]
        
        self.initial_player_hp = settings["player_hp"]

    def reset_entities(self):
        # Створюємо гравця з HP відповідно до складності
        self.player = Player(2, ROWS - 3)
        self.player.hp = self.initial_player_hp 

        self.enemies = []
        # Початкові вороги
        initial_spawns = [(COLS // 2, 1), (COLS - 3, 1), (2, 1)]
        for x, y in initial_spawns:
             self.enemies.append(Enemy(x, y))

        self.bullets = []
        self.player_bullet = None
        self.explosions = []

        self.enemy_counter = 0
        self.spawned_enemies = len(self.enemies)
        self.enemy_spawn_timer = self.ENEMY_SPAWN_INTERVAL
        self.damage_flash_timer = 0
        self.DAMAGE_FLASH_DURATION = FPS / 4


    def handle_play_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.try_shoot_player()
                elif event.key == pygame.K_ESCAPE:
                    self.state = "MENU" # Пауза / Вихід в меню

    def try_shoot_player(self):
        if self.player_bullet is None or not self.player_bullet.active:
            cell_x, cell_y = self.player.get_grid_pos()
            self.player_bullet = Bullet(cell_x, cell_y, self.player.direction, is_enemy=False)
            self.bullets.append(self.player_bullet)

    # Оновлення стану гри
    def update_play(self):
        # вороги
        for enemy in self.enemies:
            enemy.update(self.level, self.bullets)

        # спавн ворогів
        self.update_enemy_spawning()

        # кулі
        self.update_bullets()

        # попадання по ворогах
        self.resolve_enemy_hits()

        # вибухи
        for explosion in self.explosions:
            explosion.update()
        self.explosions = [e for e in self.explosions if e.active]

        # гравець
        keys = pygame.key.get_pressed()
        self.player.update()
        self.player.handle_input(keys, self.level)

        # game over
        if self.player.hp <= 0:
            self.draw_game_over()
        
        # win
        if self.enemy_counter >= self.MAX_ENEMIES_PER_LEVEL:
            self.handle_level_completion() 

    def update_enemy_spawning(self):
        self.enemy_spawn_timer -= 1

        if (self.enemy_spawn_timer <= 0
            and len(self.enemies) < self.MAX_ENEMIES_ON_SCREEN
            and self.spawned_enemies < self.MAX_ENEMIES_PER_LEVEL):

            spawn_points = self.level.enemy_spawn_points[:]
            random.shuffle(spawn_points)

            for spawn_x, spawn_y in spawn_points:
                if not self.level.can_move(spawn_x, spawn_y):
                    continue

                self.enemies.append(Enemy(spawn_x, spawn_y))
                self.spawned_enemies += 1
                break

            self.enemy_spawn_timer = self.ENEMY_SPAWN_INTERVAL

    def update_bullets(self):
        for bullet in self.bullets:
            did_damage = bullet.update(self.level, self.player)
            if did_damage:
                self.damage_flash_timer = self.DAMAGE_FLASH_DURATION

        self.bullets = [b for b in self.bullets if b.active]

    def resolve_enemy_hits(self):
        new_enemies = []

        for enemy in self.enemies:
            if not enemy.alive:
                continue

            enemy_cell_x, enemy_cell_y = enemy.get_grid_pos()
            hit = False

            for bullet in self.bullets:
                if not bullet.active or bullet.is_enemy:
                    continue

                bullet_x = int(bullet.x)
                bullet_y = int(bullet.y)

                if bullet_x == enemy_cell_x and bullet_y == enemy_cell_y:
                    bullet.active = False
                    enemy.alive = False
                    self.enemy_counter += 1
                    self.explosions.append(Explosion(enemy_cell_x, enemy_cell_y))
                    hit = True
                    break

            if not hit:
                new_enemies.append(enemy)

        self.enemies = new_enemies

    def handle_level_completion(self):
        if self.game_mode == "CAMPAIGN":
            self.draw_win_message(f"Рівень {self.campaign_level_num} ПРОЙДЕНО")
        else:
            self.draw_win_message("Ви перемогли!")

        if self.game_mode == "ARCADE":
            self.state = "MENU"
        
        elif self.game_mode == "CAMPAIGN":
            self.campaign_level_num += 1
            
            next_level_path = f"levels/level_{self.campaign_level_num}.txt"
            
            if os.path.exists(next_level_path):
                self.start_game()
            else:
                self.draw_win_message("Кампанія ПРОЙДЕНА!")
                self.state = "MENU"
    # Методи малювання

    def draw_play(self):
        self.screen.fill(BG_COLOR)

        self.level.draw(self.screen)
        self.player.draw(self.screen)

        for enemy in self.enemies:
            enemy.draw(self.screen)

        for bullet in self.bullets:
            bullet.draw(self.screen)

        for explosion in self.explosions:
            explosion.draw(self.screen)

        # трава поверх усього
        self.level.draw_grass(self.screen)

        # HUD
        self.draw_hud()

        # flash damage
        self.draw_damage_flash()

        pygame.display.flip()

    def draw_hud(self):
        hud_x = COLS * TILE
        pygame.draw.rect(self.screen, HUD_BG_COLOR, (hud_x, 0, HUD_WIDTH, HEIGHT))
        self.enemies_left = self.MAX_ENEMIES_PER_LEVEL - self.enemy_counter

        score_surf = self.font.render(f"Рахунок: {self.enemy_counter}", True, HUD_TEXT_COLOR)
        self.screen.blit(score_surf, (hud_x + 20, 20))

        on_map_surf = self.font.render(f"Ворогів на мапі: {len(self.enemies)}", True, HUD_TEXT_COLOR)
        self.screen.blit(on_map_surf, (hud_x + 20, 60))

        if self.enemies_left < 4:
            left_surf = self.font.render(f"Ворогів залишилось: {self.enemies_left}", True, HUD_TEXT_COLOR)
            self.screen.blit(left_surf, (hud_x + 20, 140))

        hp_surf = self.font.render(f"HP: {self.player.hp}", True, HUD_TEXT_COLOR)
        self.screen.blit(hp_surf, (hud_x + 20, 100))

    def draw_damage_flash(self):
        if self.damage_flash_timer > 0:
            self.damage_flash_timer -= 1
            flash = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            flash.fill((255, 0, 0, 90))
            self.screen.blit(flash, (0, 0))

    def draw_game_over(self):
        self.screen.fill((0, 0, 0))
        game_over = self.finish_font.render("GAME OVER", True, (255, 0, 0))
        self.screen.blit(game_over, (WIDTH // 2 - 80, HEIGHT // 2 - 20))
        pygame.display.flip()
        pygame.time.wait(2000)
        self.state = "MENU"
    
    def draw_win_message(self, text):
        s = pygame.Surface((WIDTH, HEIGHT))
        s.set_alpha(200)
        s.fill((0, 0, 0))
        self.screen.blit(s, (0, 0))
        
        win_surf = self.finish_font.render(text, True, (0, 255, 0))

        text_rect = win_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.screen.blit(win_surf, text_rect)
        
        pygame.display.flip()
        
        pygame.time.wait(2000)
