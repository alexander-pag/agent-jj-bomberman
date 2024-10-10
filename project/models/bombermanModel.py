from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from agents import (
    BombermanAgent,
    GrassAgent,
    MetalAgent,
    RockAgent,
    BorderAgent,
    GoalAgent,
)
from config.constants import *


class BombermanModel(Model):
    def __init__(
        self,
        width,
        height,
        map_data,
        pos_goal,
        pos_bomberman,
        number_of_agents,
        search_algorithm,
        priority,
        heuristic,
    ):
        super().__init__()
        self.num_agents = number_of_agents
        self.search_algorithm = search_algorithm
        self.heuristic = heuristic
        self.visited_cells = []
        self.final_path_cells = set()
        self.visited_ground_cells = set()
        self.grid = MultiGrid(width, height, torus=False)
        self.schedule = RandomActivation(self)
        self.running = True
        self.priority = priority
        self.pos_goal = pos_goal
        self.create_map(map_data)

        self.bomberman = BombermanAgent(1, self, pos_bomberman)

        self.grid.place_agent(self.bomberman, self.bomberman.pos)

        self.schedule.add(self.bomberman)

    def create_map(self, map_data) -> None:
        """
        Crea el mapa del modelo a partir de los datos leídos de un archivo de texto.

        Args:
            map_data (list): Lista de listas con los datos del mapa.

        Returns:
            None
        """
        for y, row in enumerate(map_data):
            for x, terrain_type in enumerate(row):
                if terrain_type == GRASS or terrain_type == BOMBERMAN:
                    cell = GrassAgent((x, y), self)
                elif terrain_type == ROCK:
                    cell = RockAgent((x, y), self)
                elif terrain_type == METAL:
                    cell = MetalAgent((x, y), self)
                elif terrain_type == BORDER:
                    cell = BorderAgent((x, y), self)
                elif terrain_type == GOAL:
                    cell = GoalAgent((x, y), self)
                else:
                    continue

                # Colocar el agente en la posición correcta
                self.grid.place_agent(cell, (x, y))
                self.schedule.add(cell)

    def step(self):
        self.schedule.step()
