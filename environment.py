import pygame
import random

# Constants
GRID_WIDTH = 30
GRID_HEIGHT = 30
OBSTACLE_PERCENTAGE = 0.2
CELL_SIZE = 20  # Size of each cell in pixels (e.g 20 = 20x20 pixels)


class Environment:
    def __init__(self):
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.place_obstacles()

    def place_obstacles(self):
        num_obstacles = int(GRID_WIDTH * GRID_HEIGHT * OBSTACLE_PERCENTAGE)
        for _ in range(num_obstacles):
            x = random.randint(0, GRID_WIDTH - 1)
            y = random.randint(0, GRID_HEIGHT - 1)
            self.grid[y][x] = 1  # 1 represents an obstacle

    def draw(self, screen):
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                color = (255, 255, 255)
                if self.grid[y][x] == 1:
                    color = (0, 0, 0)
                pygame.draw.rect(screen, color, pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((GRID_WIDTH * CELL_SIZE, GRID_HEIGHT * CELL_SIZE))
    clock = pygame.time.Clock()
    env = Environment()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((255, 255, 255))
        env.draw(screen)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
