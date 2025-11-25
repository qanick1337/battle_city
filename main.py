import pygame
import sys

pygame.init()

# Створюємо вікно
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("My Pygame Project")

clock = pygame.time.Clock()

# Головний цикл гри
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill((30, 30, 30))  # Заливаємо екран темно-сірим

    pygame.display.flip()      # Оновлюємо екран
    clock.tick(60)             # 60 FPS
