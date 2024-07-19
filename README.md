# EvoSwarmAI

EvoSwarmAI is a simulation project that demonstrates the evolution of a swarm of drones designed for search and rescue missions in a 2D grid environment with obstacles. The drones evolve to improve their cooperation, coverage efficiency, and ability to navigate through obstacles over multiple generations.

## Table of Contents
- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)

## Introduction

Swarm intelligence, inspired by the behavior of social insects such as ants and bees, can be applied to control and coordinate multiple drones. Evolutionary algorithms optimize the drones' behavior and coordination strategies by simulating natural selection processes. This project aims to demonstrate the potential of evolutionary algorithms in optimizing swarm behaviors for search and rescue missions.

## Features

- 2D grid-based environment with randomly placed obstacles
- Drones with local perception (view around their current position)
- Basic movement and obstacle avoidance algorithms for drones
- Evolutionary algorithm to optimize drone swarm behaviors

## Installation

To install and run the project, follow these steps:

1. **Clone the repository**:
    ```bash
    git clone https://github.com/yourusername/EvoSwarmAI.git
    cd EvoSwarmAI
    ```

2. **Install the required libraries**:
    ```bash
    pip install pygame deap
    ```

## Usage

To run the simulation, execute the following command:

```bash
python main.py
```

You should see a window displaying the 2D grid environment with drones moving around, avoiding obstacles, and covering the grid.

## Project Structure

```
EvoSwarmAI/
├── main.py
├── drone.py
├── environment.py
└── README.md
```

- **main.py**: Main entry point for the simulation. Combines the environment and drones, and runs the simulation loop.
- **drone.py**: Defines the Drone class with movement, local perception, and drawing capabilities.
- **environment.py**: Defines the Environment class with obstacle placement and drawing capabilities.
