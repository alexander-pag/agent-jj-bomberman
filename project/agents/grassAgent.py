from .terrainAgent import TerrainAgent


class GrassAgent(TerrainAgent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model, "C")
