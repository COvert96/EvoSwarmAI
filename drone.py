import random
import pygame

from environment import GRID_WIDTH, CELL_SIZE, GRID_HEIGHT


class Drone:
    def __init__(self, x, y, environment, perception_range):
        self.x = x
        self.y = y
        self.environment = environment
        self.perception_range = perception_range
        self.directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # Down, Right, Up, Left
        self.heading = random.choice(self.directions)  # Initial heading

    def move(self):
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # Down, Right, Up, Left
        random.shuffle(directions)
        for dx, dy in directions:
            new_x = self.x + dx
            new_y = self.y + dy
            if self.is_within_bounds(new_x, new_y) and self.environment.grid[new_y][new_x] == 0:
                self.x = new_x
                self.y = new_y
                self.heading = (dx, dy)  # Update heading

    @staticmethod
    def is_within_bounds(x, y):
        return 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT

    def get_local_view(self):
        local_view = []
        hx, hy = self.heading
        for i in range(1, self.perception_range + 1):
            for dx, dy in [(i, 0), (i, -i), (i, i)]:
                new_x = self.x + hx * dx - hy * dy
                new_y = self.y + hy * dx + hx * dy
                if self.is_within_bounds(new_x, new_y):
                    local_view.append((new_x, new_y, self.environment.grid[new_y][new_x]))
        return local_view

    def draw(self, screen):
        # Draw perception range
        local_view = self.get_local_view()
        for x, y, cell_type in local_view:
            if cell_type == 0:  # Empty cell
                color = (173, 216, 230)  # Light blue for perceived empty cells
            else:  # Obstacle cell
                color = (255, 0, 0)  # Red for perceived obstacles
            pygame.draw.rect(screen, color, pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

        # Draw the drone
        pygame.draw.rect(screen, (0, 0, 255), pygame.Rect(self.x * CELL_SIZE, self.y * CELL_SIZE, CELL_SIZE, CELL_SIZE))


if __name__ == "__main__":
    from environment import Environment

    pygame.init()
    screen = pygame.display.set_mode((GRID_WIDTH * CELL_SIZE, GRID_HEIGHT * CELL_SIZE))
    clock = pygame.time.Clock()
    env = Environment()
    drone = Drone(0, 0, env, perception_range=2)

    paused = False

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = not paused

        if not paused:
            drone.move()

        screen.fill((255, 255, 255))
        env.draw(screen)
        drone.draw(screen)
        pygame.display.flip()
        clock.tick(10)

    pygame.quit()
