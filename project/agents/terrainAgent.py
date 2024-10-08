from mesa import Agent


class TerrainAgent(Agent):
    def __init__(self, unique_id, model, terrain_type):
        super().__init__(unique_id, model)
        self.terrain_type = terrain_type

    def step(self):
        pass
