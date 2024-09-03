from typing import Callable, Dict

import torch
from torch import Tensor
from vmas.simulator.core import Agent, World, Sphere, Box, Landmark, Entity
from vmas.simulator.scenario import BaseScenario
from vmas.simulator.sensors import Lidar
from vmas.simulator.utils import Color, ScenarioUtils
import numpy as np
from config import *


class AreaCoverage(BaseScenario):
    def make_world(self, batch_dim: int, device: torch.device, **kwargs):
        self.plot_grid = False
        self.n_agents = kwargs.pop("n_agents", 4)
        self.collisions = kwargs.pop("collisions", True)
        self.grid_size = kwargs.pop("grid_size", 10)
        self.obstacle_density = kwargs.pop("obstacle_density", 0.2)
        self.lidar_range = kwargs.pop("lidar_range", 0.35)
        self.agent_radius = kwargs.pop("agent_radius", 0.1)
        self.shared_rew = kwargs.pop("shared_rew", True)
        self.min_collision_distance = kwargs.pop("min_collision_distance", 0.01)
        self.collision_penalty = kwargs.pop("collision_penalty", -1.0)
        self.revisit_penalty = kwargs.pop("revisit_penalty", -0.1)
        ScenarioUtils.check_kwargs_consumed(kwargs)

        self.world_semidim = int(self.grid_size / 2)
        self.min_distance_between_entities = self.agent_radius * 2 + 0.05

        # Each agent will have its own visited map
        self.visited_maps = {
            agent_name: torch.zeros((batch_dim, self.grid_size, self.grid_size), device=device)
            for agent_name in [f"agent_{i}" for i in range(self.n_agents)]
        }

        # Make world
        world = World(batch_dim, device, substeps=2, x_semidim=self.world_semidim, y_semidim=self.world_semidim)

        # Add agents
        for i in range(self.n_agents):
            agent = Agent(
                name=f"agent_{i}",
                collide=True,
                color=(0.1, 0.1, 0.8),  # Blue color for drones
                shape=Sphere(radius=self.agent_radius),
                render_action=True,
                sensors=([
                             Lidar(
                                 world,
                                 n_rays=12,
                                 max_range=self.lidar_range,
                                 entity_filter=lambda e: isinstance(e, Entity)
                             ),
                         ]
                         if self.collisions
                         else None
                         )
            )
            agent.pos_rew = torch.zeros(batch_dim, device=device)
            agent.agent_revisit_rew = agent.pos_rew.clone()
            agent.agent_collision_rew = agent.pos_rew.clone()
            world.add_agent(agent)

        # Add obstacles
        self.add_obstacles(world, batch_dim, device)

        # Initialize reward trackers
        self.pos_rew = torch.zeros(batch_dim, device=device)

        return world

    def add_obstacles(self, world, batch_dim, device):
        num_obstacles = int(self.obstacle_density * self.grid_size ** 2)
        for _ in range(num_obstacles):
            obstacle = Landmark(
                name="obstacle",
                collide=True,
                color=(0.5, 0.5, 0.5),  # Gray color for obstacles
                shape=Box(length=self.agent_radius * 2, width=self.agent_radius * 2),
            )
            world.add_landmark(obstacle)

    def reset_world_at(self, env_index: int = None):
        # Reset visited maps
        for m in self.visited_maps.values():
            if env_index is None:
                m.fill_(0)
            else:
                m[env_index].fill_(0)

        # Spawn agents and obstacles at random positions
        ScenarioUtils.spawn_entities_randomly(
            self.world.agents + self.world.landmarks,
            self.world,
            env_index,
            self.min_distance_between_entities,
            (-self.world_semidim, self.world_semidim),
            (-self.world_semidim, self.world_semidim)
        )

    def reward(self, agent: Agent):
        is_first = agent == self.world.agents[0]

        if is_first:
            self.pos_rew[:] = 0

            for a in self.world.agents:
                self.pos_rew += self.calculate_mapping_progress(a)
                a.agent_collision_rew[:] = 0
                a.agent_revisit_rew[:] = 0

            # Penalise collisions and revisits
            for i, a in enumerate(self.world.agents):
                a.agent_revisit_rew += self.check_revisits(a)
                for j, b in enumerate(self.world.agents):
                    if i <= j:
                        continue
                    if self.world.collides(a, b):
                        distance = self.world.get_distance(a, b)
                        a.agent_collision_rew[
                            distance <= self.min_collision_distance
                            ] += self.collision_penalty
                        b.agent_collision_rew[
                            distance <= self.min_collision_distance
                            ] += self.collision_penalty

        pos_reward = self.pos_rew if self.shared_rew else agent.pos_rew
        return pos_reward + agent.agent_collision_rew

    def calculate_mapping_progress(self, agent):
        # Convert the agent's position to grid coordinates
        x, y = self.position_to_grid(agent.state.pos)

        agent_name = agent.name
        agent.visited_map = self.visited_maps[agent_name]

        # Check if the current cell has been visited by this agent
        if agent.visited_map == 1:
            return 0.0
        else:
            # Update the visited map for the agent
            visited_map[:, x, y] = 1
            return 1.0

    def check_revisits(self, agent: Agent):
        # Apply a penalty if the agent revisits an area it has already mapped
        x, y = self.position_to_grid(agent.state.pos)
        agent_name = agent.name
        revisit_penalty = (self.visited_maps[agent_name][:, x, y] == 1).float() * self.revisit_penalty
        return revisit_penalty

    def position_to_grid(self, position):
        # Convert continuous position to discrete grid index
        x = ((position[:, 0] + self.world_semidim) / (2 * self.world_semidim) * self.grid_size).long()
        y = ((position[:, 1] + self.world_semidim) / (2 * self.world_semidim) * self.grid_size).long()
        return x, y

    def observation(self, agent):
        return torch.cat(
            [
                agent.state.pos,
                agent.state.vel,
            ]
            + (
                [agent.sensors[0]._max_range - agent.sensors[0].measure()]
                if self.collisions
                else []
            ),
            dim=-1
        )

    def done(self):
        # Combine all visited maps from all agents to see if every cell has been visited
        combined_visited_map = torch.zeros_like(next(iter(self.visited_maps.values())))

        for visited_map in self.visited_maps.values():
            combined_visited_map = torch.logical_or(combined_visited_map, visited_map)

        # Check if all cells have been visited in each batch
        all_cells_visited = combined_visited_map.all(dim=(-2, -1))  # Checks across the grid dimensions

        return all_cells_visited

    def info(self, agent: Agent) -> Dict[str, Tensor]:
        return {
            "mapping_progress": self.pos_rew,
        }
