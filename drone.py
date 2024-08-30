import math
import random
import pygame

from agents import MultiAgent
from environment import GRID_WIDTH, CELL_SIZE, GRID_HEIGHT


class SharedMemory:
    def __init__(self, width, height):
        self.memory = [[-1 for _ in range(width)] for _ in range(height)]  # -1 indicates unexplored

    def update_memory(self, x, y, value):
        self.memory[y][x] = value

    def get_memory(self, x, y):
        return self.memory[y][x]


class Drone:
    def __init__(self, x, y, environment, perception_range, shared_memory, fov_degrees=120):
        self.x = x
        self.y = y
        self.environment = environment
        self.perception_range = perception_range
        self.fov_degrees = fov_degrees
        self.shared_memory = shared_memory
        self.directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # Down, Right, Up, Left
        self.heading = random.choice(self.directions)  # Initial heading

    def update_shared_memory(self):
        local_view = self.get_local_view()
        for x, y, cell_type in local_view:
            self.shared_memory.update_memory(x, y, cell_type)

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
                break

    @staticmethod
    def is_within_bounds(x, y):
        return 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT

    def cast_ray(self, angle):
        x, y = self.x, self.y
        sin_angle = math.sin(angle)
        cos_angle = math.cos(angle)
        for i in range(1, self.perception_range + 1):
            x += cos_angle
            y += sin_angle
            grid_x, grid_y = int(round(x)), int(round(y))
            if not self.is_within_bounds(grid_x, grid_y):
                break
            if self.environment.grid[grid_y][grid_x] == 1:  # Stop at obstacle
                yield grid_x, grid_y, 1
            yield grid_x, grid_y, 0  # Visible empty cell

    def get_local_view(self):
        local_view = []
        # Convert FOV to radians
        half_fov_radians = math.radians(self.fov_degrees / 2)

        # Get the angle of the current heading
        heading_angle = math.atan2(self.heading[1], self.heading[0])

        # Calculate range of angles within the FOV
        start_angle = heading_angle - half_fov_radians
        end_angle = heading_angle + half_fov_radians

        # Cast rays within FOV
        num_rays = 20  # Number of rays to cast within FOV
        angle_increment = (end_angle - start_angle) / (num_rays - 1)

        # angles = [i * math.pi / 4 for i in range(8)]  # 8 directions
        for i in range(num_rays):
            angle = start_angle + i * angle_increment
            for cell in self.cast_ray(angle):
                local_view.append(cell)
                if cell[2] == 1:  # Stop at obstacle
                    break
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


class DroneController:
    def __init__(self, drone: Drone, agent: MultiAgent):
        self.drone = drone
        self.agent = agent

    def take_action(self):
        state = self.drone.get_state_representation()
        action = self.agent.choose_action(state)
        reward = self.drone.perform_action(action)
        next_state = self.drone.get_state_representation()
        self.agent.learn(state, action, reward, next_state)


if __name__ == "__main__":
    from environment import Environment

    pygame.init()
    screen = pygame.display.set_mode((GRID_WIDTH * CELL_SIZE, GRID_HEIGHT * CELL_SIZE))
    clock = pygame.time.Clock()
    env = Environment()
    drone = Drone(0, 0, env, perception_range=1)
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
            drone.update_shared_memory()

        screen.fill((255, 255, 255))
        env.draw(screen)
        drone.draw(screen)
        pygame.display.flip()
        clock.tick(10)

    pygame.quit()
