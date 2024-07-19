import random
import pygame

from environment import Environment, GRID_WIDTH, CELL_SIZE, GRID_HEIGHT


class Drone:
    def __init__(self, x, y, environment):
        self.x = x
        self.y = y
        self.environment = environment

    def move(self):
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # Down, Right, Up, Left
        random.shuffle(directions)
        for dx, dy in directions:
            new_x = self.x + dx
            new_y = self.y + dy
            if GRID_WIDTH > new_x >= 0 == self.environment.grid[new_y][new_x] and 0 <= new_y < GRID_HEIGHT:
                self.x = new_x
                self.y = new_y
                break

    def draw(self, screen):
        pygame.draw.rect(screen, (0, 0, 255), pygame.Rect(self.x * CELL_SIZE, self.y * CELL_SIZE, CELL_SIZE, CELL_SIZE))


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((GRID_WIDTH * CELL_SIZE, GRID_HEIGHT * CELL_SIZE))
    clock = pygame.time.Clock()
    env = Environment()
    drone = Drone(0, 0, env)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((255, 255, 255))
        env.draw(screen)
        drone.move()
        drone.draw(screen)
        pygame.display.flip()
        clock.tick(10)

    pygame.quit()
