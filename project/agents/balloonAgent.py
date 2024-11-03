import random
from mesa import Agent
from .metalAgent import MetalAgent
from .rockAgent import RockAgent
from .borderAgent import BorderAgent
from .bombermanAgent import BombermanAgent


class BalloonAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        # darle una posición inicial aleatoria pero no en un obstáculo
        x = self.random.randrange(model.grid.width)
        y = self.random.randrange(model.grid.height)
        self.pos = (x, y)
        while self.is_obstacle(self.pos):
            x = self.random.randrange(model.grid.width)
            y = self.random.randrange(model.grid.height)
            self.pos = (x, y)

        self.model.grid.place_agent(self, self.pos)

    def step(self):
        self.move()

    def move(self):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=False, include_center=False
        )
        new_position = self.random.choice(possible_steps)
        if not self.is_obstacle(new_position):
            print("moviendo globo a: ", new_position)
            self.model.grid.move_agent(self, new_position)
            self.pos = new_position
            self.detect_bomberman()

    def is_obstacle(self, pos):
        cellmates = self.model.grid.get_cell_list_contents([pos])
        for agent in cellmates:
            if (
                isinstance(agent, BorderAgent)
                or isinstance(agent, RockAgent)
                or isinstance(agent, MetalAgent)
            ):
                return True
        return False

    # detectar si hay un bomberman en la misma posición que el globo y terminar la simulación
    def detect_bomberman(self):
        cellmates = self.model.grid.get_cell_list_contents([self.pos])
        for agent in cellmates:
            if isinstance(agent, BombermanAgent):
                print("¡Bomberman ha sido capturado!")
                self.model.running = False
                break
