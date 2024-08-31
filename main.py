import random
import pygame
from config import GRID_WIDTH, GRID_HEIGHT, CELL_SIZE, NUM_DRONES, PERCEPTION_RANGE
from environment import Environment
from drone import SharedMemory, Drone


def draw_shared_memory(screen, shared_memory):
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            memory_value = shared_memory.get_memory(x, y)
            if memory_value == -1:  # Unexplored cell
                colour = (211, 211, 211)  # Fog of war
            elif memory_value == 1:  # Obstacle
                colour = (0, 0, 0)
            elif memory_value == 0:  # (Explored) Empty cell
                colour = (255, 255, 255)
            pygame.draw.rect(screen, colour, pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))


def main():
    # Initialise the environment
    environment = Environment()

    # Initialise shared memory
    shared_memory = SharedMemory(GRID_WIDTH, GRID_HEIGHT)

    # Initialise drones and agents
    drones = []
    for _ in range(NUM_DRONES):
        x, y = 0, 0
        drone = Drone(x, y, environment, PERCEPTION_RANGE, shared_memory)
        drones.append(drone)

    pygame.init()
    screen = pygame.display.set_mode((GRID_WIDTH * CELL_SIZE, GRID_HEIGHT * CELL_SIZE))
    clock = pygame.time.Clock()

    SHARED_MEMORY_VIEW = True

    # Initialise Pygame windows
    screen_env = pygame.display.set_mode((GRID_WIDTH * CELL_SIZE, GRID_HEIGHT * CELL_SIZE))
    screen_memory = pygame.display.set_mode((GRID_WIDTH * CELL_SIZE, GRID_HEIGHT * CELL_SIZE))

    # Display shared memory or actual environment w/ drones
    pygame.display.set_caption('Shared Memory') if SHARED_MEMORY_VIEW else pygame.display.set_caption(
        'Environment and Drones')

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
            for drone in drones:
                drone.move()
                drone.update_shared_memory()

        screen_env.fill((255, 255, 255))
        environment.draw(screen)
        for drone in drones:
            drone.draw(screen_env)

        if SHARED_MEMORY_VIEW:
            # Draw shared memory
            screen_memory.fill((255, 255, 255))  # Clear the shared memory window
            for drone in drones:
                drone.draw(screen_memory)
            draw_shared_memory(screen_memory, shared_memory)

        pygame.display.flip()
        clock.tick(10)

    pygame.quit()

    # # Define the PPO model
    # model = PPO('CnnPolicy', env, verbose=1, tensorboard_log="./ppo_marl_tensorboard/")
    #
    # # Train the model
    # model.learn(total_timesteps=100000)
    #
    # # Save the model
    # model.save("ppo_marl_drone")


if __name__ == "__main__":
    main()
