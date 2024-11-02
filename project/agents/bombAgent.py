from mesa import Agent
from agents.rockAgent import RockAgent


class BombAgent(Agent):
    def __init__(self, unique_id, model, bomb_position):
        super().__init__(unique_id, model)
        self.timer = 3  # Número de pasos antes de explotar.
        self.bomb_position = bomb_position

    def step(self):
        if self.timer > 0:
            self.timer -= 1
        else:
            self.detonate()

    def detonate(self):
        # Remover la roca y luego la bomba misma
        cell_contents = self.model.grid.get_cell_list_contents([self.bomb_position])
        for agent in cell_contents:
            if isinstance(agent, RockAgent):
                self.model.grid.remove_agent(agent)
        # Remueve la bomba de la cuadrícula
        self.model.grid.remove_agent(self)
