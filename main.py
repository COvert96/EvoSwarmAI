import random

import pygame
from environment import Environment, GRID_WIDTH, CELL_SIZE, GRID_HEIGHT
from drone import Drone

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((GRID_WIDTH * CELL_SIZE, GRID_HEIGHT * CELL_SIZE))
    clock = pygame.time.Clock()
    env = Environment()
    drones = [Drone(random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1), env) for _ in range(10)]

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((255, 255, 255))
        env.draw(screen)
        for drone in drones:
            drone.move()
            drone.draw(screen)
        pygame.display.flip()
        clock.tick(10)

    pygame.quit()
