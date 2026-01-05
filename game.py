# game.py
import sys
import os
import random
import pygame
import assets
import save_manager

from enemies.enemy import Enemy
from settings import (
    WIDTH, HEIGHT, BG_COLOR, FPS, ROWS, COLS, HUD_WIDTH,
    HUD_TEXT_COLOR, TILE, HUD_BG_COLOR
)

from level_builder import Level
from player import Player
from bullet import Bullet
from explosion import Explosion
from bonus import Bonus
from base import Base


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

        self.stats_font = pygame.font.SysFont("Consolas", 15)

        # Рівні складності
        self.difficulty_presets = {
            "EASY": {"player_hp":1, "lives": 5, "max_enemies":5, "spawn_speed": FPS*4, "max_enemies_on_map":3},
            "NORMAL": {"player_hp": 1, "lives": 3, "max_enemies": 10, "spawn_speed": FPS * 3, "max_enemies_on_map":5},
            "HARD":   {"player_hp": 1, "lives": 2, "max_enemies": 20, "spawn_speed": FPS * 2, "max_enemies_on_map":10},
            "HARDCORE":   {"player_hp": 1, "lives": 1, "max_enemies": 30, "spawn_speed": FPS * 1, "max_enemies_on_map":20}
        }

        self.game_data = save_manager.load_data()

        # Поточні вибори в меню
        self.selected_difficulty = "NORMAL"
        self.game_mode = "CAMPAIGN"

        self.update_level_num_from_save()
        
        # Встановлюємо рівень відповідно до збереження для NORMAL
        self.campaign_level_num = self.game_data["campaign_progress"].get(self.selected_difficulty, 1)
        self.default_level_num = self.game_data["classic_progress"].get(self.selected_difficulty, 1)

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
        self.base = None
        self.player = None
        self.enemies = []
        self.bullets = []
        self.explosions = []
        self.bonuses = []
        self.player_respawn_timer = 0
        self.shovel_timer = 0

    def get_progress_key(self):
        if self.game_mode == "DEFAULT":
            return f"DEFAULT_{self.selected_difficulty}"
        else:
            return self.selected_difficulty
        
    def update_level_num_from_save(self):
        if self.game_mode == "DEFAULT":
            dict_key = "classic_progress"
            self.default_level_num = self.game_data[dict_key].get(self.selected_difficulty, 1)
        else:
            dict_key = "campaign_progress"
            self.campaign_level_num = self.game_data[dict_key].get(self.selected_difficulty, 1) 
        

    def reset(self):
        # Створення сутностей для геймплею
        self.player = Player((self.player.spawn))


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

            elif self.state == "PAUSE":
                self.handle_pause_events()
                self.draw_pause()

        pygame.quit()
        sys.exit()

    # Menu-events
    def handle_menu_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a: self.game_mode = "ARCADE"
                elif event.key == pygame.K_c: self.game_mode = "CAMPAIGN"
                elif event.key == pygame.K_d: self.game_mode = "DEFAULT"
                
                elif event.key == pygame.K_1: self.selected_difficulty = "EASY"
                elif event.key == pygame.K_2: self.selected_difficulty = "NORMAL"
                elif event.key == pygame.K_3: self.selected_difficulty = "HARD"
                elif event.key == pygame.K_4: self.selected_difficulty = "HARDCORE"
                
                # Оновлюємо відображення рівня при зміні режиму чи складності
                if event.key in (pygame.K_a, pygame.K_c, pygame.K_d, pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4):
                    self.update_level_num_from_save()

                elif event.key == pygame.K_RETURN: self.start_game()
                elif event.key == pygame.K_ESCAPE: self.running = False

    def handle_pause_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if event.type == pygame.KEYDOWN:
                self.state = "PLAY"

    def draw_menu(self):
        self.screen.fill((20, 20, 20))

        title = self.title_font.render("BATTLE CITY", True, (255, 215, 0))
        self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 80))
      
        # 1. Режим гри
        mode_text_str = f"Режим гри: < {self.game_mode} >"
        if self.game_mode == "DEFAULT": m_color = (0, 255, 0)
        elif self.game_mode == "CAMPAIGN": m_color = (255, 200, 0)
        else: m_color = (0, 255, 255)
        self.draw_text_centered(mode_text_str, 200, m_color)
        self.draw_text_centered("(Натисніть A - Arcade, C - Campaign, D - Default", 230, (100, 100, 100))


        # 2. Складність
        diff_text_str = f"Складність: < {self.selected_difficulty} >"
        diff_color = (255, 0, 0) if self.selected_difficulty == "HARDCORE" else (0, 255, 0)
        self.draw_text_centered(diff_text_str, 280, diff_color)
        self.draw_text_centered("(Натисніть 1-Easy, 2-Normal, 3-Hard )", 310, (100, 100, 100))

        # 3. Кнопка Старт
        blink_speed = pygame.time.get_ticks() // 500  # Блимання раз на пів секунди
        if blink_speed % 2 == 0:
            self.draw_text_centered("НАТИСНІТЬ [ENTER] ЩОБ ПОЧАТИ", 400, (255, 255, 255))
       
        # Якщо обрано Кампанію або Класику - показуємо прогрес
        if self.game_mode == "DEFAULT":
            # Показуємо default_level_num
            lvl_info = f"Прогрес (Classic): Рівень {self.default_level_num}"
            self.draw_text_centered(lvl_info, HEIGHT - 60, (0, 255, 0))
            
        elif self.game_mode == "CAMPAIGN":
            # Показуємо campaign_level_num
            lvl_info = f"Прогрес (Campaign): Рівень {self.campaign_level_num}"
            self.draw_text_centered(lvl_info, HEIGHT - 60, (255, 215, 0))
            
        else:
            self.draw_text_centered("Аркада: Безкінечна війна", HEIGHT - 60, (0, 255, 255))

        # Загальна статистика
        stats = self.game_data["stats"]
        stat_text = f"Ігор: {stats['total_games']} | Вбито: {stats['total_kills']} | Смертей: {stats['deaths']}"
        stat_surf = self.stats_font.render(stat_text, True, (80, 80, 80))
        self.screen.blit(stat_surf, (10, HEIGHT - 20))

        pygame.display.flip()

    def draw_text_centered(self, text, y, color):
        surf = self.menu_font.render(text, True, color)
        x = WIDTH // 2 - surf.get_width() // 2
        self.screen.blit(surf, (x, y))

    # Game-events
    def start_game(self):
        save_manager.add_stats(games=1)
        self.game_data = save_manager.load_data()
        self.apply_difficulty_settings()
        self.level_enemy_queue = []

        # 1. ARCADE
        if self.game_mode == "ARCADE":
            self.level.generate_valid_level()
            for num in range(self.MAX_ENEMIES_PER_LEVEL):
                t = random.choice(["BASIC", "FAST", "ARMOR", "SNIPER"])
                self.level_enemy_queue.append(t)
        
        # 2. DEFAULT (Classic) - Використовуємо default_level_num
        elif self.game_mode == "DEFAULT":
            # Тут використовуємо self.default_level_num
            path = f"classic_levels/level_{self.default_level_num}.txt"

            if not os.path.exists(path):
                print(f"Classic рівень {path} не знайдено! Генеруємо рандом.")
                self.level.generate_valid_level()
                self.level_enemy_queue = ["BASIC"] * self.MAX_ENEMIES_PER_LEVEL
            else:
                self.level_enemy_queue = self.level.load_from_file(path)
            self.MAX_ENEMIES_PER_LEVEL = len(self.level_enemy_queue)

        # 3. CAMPAIGN - Використовуємо campaign_level_num
        else:
            path = f"levels/level_{self.campaign_level_num}.txt"
            if not os.path.exists(path):
                print(f"Рівень {path} не знайдено! Генеруємо рандом.")
                self.level.generate_valid_level()
                self.level_enemy_queue = ["BASIC"] * self.MAX_ENEMIES_PER_LEVEL
            else:
                self.level_enemy_queue = self.level.load_from_file(path) 

            self.MAX_ENEMIES_PER_LEVEL = len(self.level_enemy_queue)

        self.reset_entities()
        self.state = "PLAY"

    def apply_difficulty_settings(self):
        settings = self.difficulty_presets[self.selected_difficulty]
        
        self.MAX_ENEMIES_ON_SCREEN = settings["max_enemies_on_map"]
        self.MAX_ENEMIES_PER_LEVEL = settings["max_enemies"]
        self.ENEMY_SPAWN_INTERVAL = settings["spawn_speed"]

        self.initial_player_lives = settings["lives"]
        self.initial_player_hp = settings["player_hp"]
        

    def reset_entities(self):
        if self.game_mode == "DEFAULT":
            base_x = 8
            base_y = ROWS - 2
            self.base = Base(base_x, base_y)

            spawn_x = base_x - 2 

        else:   
            self.base = None # Бази немає
            spawn_x = COLS // 2 # Спавн по центру

        spawn_y = ROWS - 2 # Завжди знизу

        

        self.player = Player(spawn_x, spawn_y, lives=self.initial_player_lives)
        self.player.hp = self.initial_player_hp 

        if 0 <= spawn_y < ROWS and 0 <= spawn_x < COLS:
            self.level.grid[spawn_y][spawn_x] = 0

        self.enemies = []
        self.bullets = []
        self.player_bullet = None
        self.explosions = []
        self.bonuses = []

        self.enemy_counter = 0
        self.spawned_enemies = len(self.enemies)
        self.enemy_spawn_timer = 0
        self.damage_flash_timer = 0
        self.DAMAGE_FLASH_DURATION = FPS / 4

        self.showel_timer = 0

    def handle_play_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE: 
                    if self.player.hp > 0: self.try_shoot_player()
                elif event.key == pygame.K_ESCAPE: self.state = "MENU"
                elif event.key == pygame.K_p: self.state = "PAUSE"

    def try_shoot_player(self):
        if self.player_bullet is None or not self.player_bullet.active:
            cell_x, cell_y = self.player.get_grid_pos()
            self.player_bullet = Bullet(cell_x, cell_y, self.player.direction, is_enemy=False)
            self.bullets.append(self.player_bullet)

    def set_base_protection(self, tile_type):
        if not self.base:
            return

        bx, by = self.base.x, self.base.y
        

        positions = [
            (bx - 1, by),   
            (bx - 1, by - 1),
            (bx,     by - 1), 
            (bx + 1, by - 1), 
            (bx + 1, by) 
        ]

        for x, y in positions:
            if 0 <= x < COLS and 0 <= y < ROWS:
                self.level.grid[y][x] = tile_type

    # Оновлення стану гри
    def update_play(self):
        # вороги
        for enemy in self.enemies:
            enemy.update(self.level, self.bullets, self.player)

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

        for bonus in self.bonuses:
            bonus.timer -=1

            if not bonus.timer:
                self.bonuses.remove(bonus)
            if self.player.x == bonus.x and self.player.y == bonus.y:
                self.apply_bonus(bonus.type, self.player)
                self.bonuses.remove(bonus)

        if self.shovel_timer > 0:
            self.shovel_timer -= 1

            if self.shovel_timer == 0:
                self.set_base_protection(1) # Повертаємо 1 = ЦЕГЛА

        # game over
        if self.player.hp <= 0:

            if self.player_respawn_timer > 0:
                self.player_respawn_timer -= 1
            else:
                # Якщо залишилися життя, респавнемо гравця
                if self.player.lives > 0:
                    self.player.respawn() 
                else:
                    self.draw_game_over() 
        
        # win
        if self.enemy_counter >= self.MAX_ENEMIES_PER_LEVEL:
            self.handle_level_completion()  

    def update_enemy_spawning(self):
        self.enemy_spawn_timer -= 1

        # Умови спавну:
        # На екрані є місце (< MAX_ON_SCREEN)
        # У черзі ще є вороги (self.level_enemy_queue не пуста)
        
        if (self.enemy_spawn_timer <= 0 
            and len(self.enemies) < self.MAX_ENEMIES_ON_SCREEN 
            and len(self.level_enemy_queue) > 0):

            spawn_points = self.level.enemy_spawn_points[:]
            random.shuffle(spawn_points)

            for spawn_x, spawn_y in spawn_points:
                if not self.level.can_move(spawn_x, spawn_y):
                    continue
                
                # --- БЕРЕМО НАСТУПНОГО ВОРОГА З ЧЕРГИ ---
                next_enemy_type = self.level_enemy_queue.pop(0) # Забираємо першого
                
                self.enemies.append(Enemy(spawn_x, spawn_y, next_enemy_type))
                self.spawned_enemies += 1
                break

            self.enemy_spawn_timer = self.ENEMY_SPAWN_INTERVAL

    def update_bullets(self):
        for bullet in self.bullets:
            did_die = bullet.update(self.level, self.player)
            
            if did_die:
                self.damage_flash_timer = self.DAMAGE_FLASH_DURATION

            if self.game_mode == "DEFAULT" and self.base and self.base.alive:
                if bullet.check_base_collision(self.base):
                    self.explosions.append(Explosion(self.base.x, self.base.y))
                    self.draw_game_over()
                    return

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
                    hit = True

                    is_dead = enemy.take_damage()
                    
                    if is_dead:
                        self.enemy_counter += 1
                        self.explosions.append(Explosion(enemy_cell_x, enemy_cell_y))


                        chance = random.random()
                        bonus_to_spawn = None
                        
                        if enemy.type == "BASIC":
                            if self.game_mode == "DEFAULT":
                                if chance < 0.15:     bonus_to_spawn = "SHOVEL"  # 15%
                                elif chance < 0.20:   bonus_to_spawn = "SHIELD"  # 5% (від 0.15 до 0.20)
                            else:
                                if chance < 0.05:     bonus_to_spawn = "GRENADE" # 5%
                        
                        elif enemy.type == "FAST":
                            if chance < 0.15:         bonus_to_spawn = "FREEZE"  # 15%
                            elif chance < 0.20:       bonus_to_spawn = "GRENADE" # 5%

                        elif enemy.type == "SNIPER":
                            if chance < 0.10:         bonus_to_spawn = "GRENADE" # 10%
                            elif chance < 0.15:       bonus_to_spawn = "SHOVEL"  # 5% 
                            elif chance < 0.18:       bonus_to_spawn = "HEART"   # 3% 

                        elif enemy.type == "ARMOR":
                            if chance < 0.10:         bonus_to_spawn = "HEART"   # 10% 
                            elif chance < 0.25:       bonus_to_spawn = "SHIELD"  # 15% 
                            elif chance < 0.35:       bonus_to_spawn = "SHOVEL"  # 10%

                        if bonus_to_spawn:
                            self.bonuses.append(Bonus(bullet_x, bullet_y, bonus_to_spawn))
                    break

            if enemy.alive:
                new_enemies.append(enemy)

        self.enemies = new_enemies

    def handle_level_completion(self):
        save_manager.add_stats(kills=self.enemy_counter)
        
        if self.game_mode == "DEFAULT":
            self.draw_win_message(f"CLASSIC {self.default_level_num} ПРОЙДЕНО")
            
            next_level = self.default_level_num + 1
            if self.default_level_num == 5:
                self.draw_win_message("КЛАСИКУ ЗАВЕРШЕНО! НОВА ГРА+")
                next_level = 1
            
            # Зберігаємо в classic_progress
            save_manager.update_progress("DEFAULT", self.selected_difficulty, next_level)
            self.game_data = save_manager.load_data()
            
            self.default_level_num = next_level
            
            path = f"classic_levels/level_{self.default_level_num}.txt"
            if os.path.exists(path):
                self.start_game()
            else:
                self.draw_win_message("Рівень не знайдено!")
                self.state = "MENU"

        elif self.game_mode == "CAMPAIGN":
            self.draw_win_message(f"Рівень {self.campaign_level_num} ПРОЙДЕНО")
            
            next_level = self.campaign_level_num + 1
            if self.campaign_level_num == 10:
                self.draw_win_message("КАМПАНІЮ ЗАВЕРШЕНО!")
                next_level = 1

            # Зберігаємо в campaign_progress
            save_manager.update_progress("CAMPAIGN", self.selected_difficulty, next_level)
            self.game_data = save_manager.load_data()

            self.campaign_level_num = next_level
            
            path = f"levels/level_{self.campaign_level_num}.txt"
            if os.path.exists(path):
                self.start_game()
            else:
                self.draw_win_message("Рівень не знайдено!")
                self.state = "MENU"

        else:
            self.draw_win_message("Ви перемогли! Наступний раунд...")
            self.start_game()
  
    def apply_bonus(self, bonus_type, player):
        if bonus_type == "GRENADE":
            for enemy in self.enemies:
                enemy.alive = False 
                self.explosions.append(Explosion(enemy.x, enemy.y))
            self.enemy_counter += len(self.enemies)
            self.enemies = []

        elif bonus_type == "SHIELD":
            player.invincible += FPS*10
        elif bonus_type == "HEART":
            player.hp +=1
        elif bonus_type == "FREEZE":
            for enemy in self.enemies:
                enemy.move_timer += FPS*2
                enemy.shoot_timer += FPS*2
        elif bonus_type == "SHOVEL":
            self.shovel_timer = FPS * 10  # 10 секунд
            self.set_base_protection(2)   # 2 = СТАЛЬ

    

    # Методи малювання
    def draw_play(self, flip=True):
        self.screen.fill(BG_COLOR)

        self.level.draw(self.screen)
        self.player.draw(self.screen)


        if self.game_mode == "DEFAULT" and self.base:
             self.base.draw(self.screen)
    
        for enemy in self.enemies:
            enemy.draw(self.screen)

        for bullet in self.bullets:
            bullet.draw(self.screen)

        for explosion in self.explosions:
            explosion.draw(self.screen)
        
        for bonus in self.bonuses:
            bonus.draw(self.screen)

        # трава поверх усього
        self.level.draw_grass(self.screen)

        # HUD
        self.draw_hud()

        # flash damage
        self.draw_damage_flash()

        pygame.display.flip()

        if flip:
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
            left_surf = self.font.render(f"Залишилось ворогів: {self.enemies_left}", True, HUD_TEXT_COLOR)
            self.screen.blit(left_surf, (hud_x + 20, 180))

        hp_surf = self.font.render(f"Життів: {self.player.lives}", True, HUD_TEXT_COLOR)
        self.screen.blit(hp_surf, (hud_x + 20, 100))

        hp_val_surf = self.font.render(f"HP: {self.player.hp}", True, HUD_TEXT_COLOR)
        self.screen.blit(hp_val_surf, (hud_x + 20, 140))

        if self.game_mode == "DEFAULT":
            lvl_text = f"Рівень класики: {self.default_level_num}"
            color = (0, 255, 0) # Зелений для класики
        elif self.game_mode == "CAMPAIGN":
            lvl_text = f"Рівень кампанії: {self.campaign_level_num}"
            color = (255, 215, 0) # Золотий для кампанії
        else:
            lvl_text = "ARCADE"
            color = (0, 255, 255)

        lvl_surf = self.font.render(lvl_text, True, color)
        self.screen.blit(lvl_surf, (hud_x + 10, HEIGHT - 40))

    def draw_pause(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        
        overlay.fill((0, 0, 0, 50)) 
        
        self.screen.blit(overlay, (0, 0))
        pause_text = self.title_font.render("ПАУЗА", True, (255, 255, 255))
        text_rect = pause_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.screen.blit(pause_text, text_rect)
        
        sub_text = self.font.render("Натисніть БУДЬ-ЯКУ клавішу для продовження", True, (200, 200, 200))
        sub_rect = sub_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40))
        self.screen.blit(sub_text, sub_rect)

        pygame.display.flip()

    def draw_damage_flash(self):
        if self.damage_flash_timer > 0:
            self.damage_flash_timer -= 1
            flash = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            flash.fill((255, 0, 0, 90))
            self.screen.blit(flash, (0, 0))

    def draw_game_over(self):
        save_manager.add_stats(kills=self.enemy_counter, deaths=1)
        self.screen.fill((0, 0, 0))
        
        reason = None

        if self.game_mode == "DEFAULT" and self.base and not self.base.alive:
            reason = "База знищена"

        elif self.player.lives <= 0:
            reason = "Ви програли"

        go_surf = self.finish_font.render("GAME OVER", True, (255, 0, 0))
        r_surf = self.font.render(reason, True, (200, 200, 200))

        self.screen.blit(go_surf, (WIDTH // 2 - go_surf.get_width()//2, HEIGHT // 2 - 40))
        self.screen.blit(r_surf, (WIDTH // 2 - r_surf.get_width()//2, HEIGHT // 2 + 10))

        pygame.display.flip()
        pygame.time.wait(3000)

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
