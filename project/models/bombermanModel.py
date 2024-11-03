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
    BalloonAgent,
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
        balloons
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
        self.balloons = balloons
        self.pos_goal = pos_goal
        self.create_map(map_data)

        self.bomberman = BombermanAgent(1, self, pos_bomberman)

        self.grid.place_agent(self.bomberman, self.bomberman.pos)

        self.schedule.add(self.bomberman)

        for i in range(self.balloons):
            balloon = BalloonAgent(i + 2, self)
            self.grid.place_agent(balloon, balloon.pos)
            self.schedule.add(balloon)

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

    def step(self) -> None:
        self.schedule.step()

        agents_in_cell = self.grid.get_cell_list_contents(self.bomberman.pos)
        
        for a in agents_in_cell:
            if isinstance(a, BalloonAgent):
                print("Bomberman ha sido derrotado")
                self.running = False
        
        # Verificar si Bomberman ha llegado a la salida
        if self.bomberman.pos == self.pos_goal:
            self.running = False

    def throw_bomb(self, current_pos, target_pos):
        """Destruye una roca y muestra animación de bomba"""
        cell_contents = self.grid.get_cell_list_contents(target_pos)
        rock_found = any(isinstance(agent, RockAgent) for agent in cell_contents)

        if rock_found:
            # Primero remover la roca
            for agent in cell_contents:
                if isinstance(agent, RockAgent):
                    self.grid.remove_agent(agent)
                    break
            from agents import BombAgent
            # Crear y colocar bomba en la posición del objetivo
            bomb = BombAgent(self.next_id(), self, target_pos)
            self.grid.place_agent(bomb, target_pos)
            
            # Crear césped después de un breve delay
            grass_agent = GrassAgent(target_pos, self)
            self.grid.place_agent(grass_agent, target_pos)
            self.schedule.add(grass_agent)

            # La bomba debe aparecer en una capa superior
            return bomb  # Retornamos la bomba para poder eliminarla después

    def next_id(self) -> int:
        return super().next_id()


