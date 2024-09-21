from mesa import Agent


# Crear una clase base para los agentes de terreno
class TerrainAgent(Agent):
    def __init__(self, unique_id, model, terrain_type):
        super().__init__(unique_id, model)
        self.terrain_type = terrain_type  # Tipo de terreno: 'C', 'R', 'M'

    def step(self):
        pass
