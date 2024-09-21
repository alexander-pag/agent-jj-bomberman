from .terrainAgent import TerrainAgent


class MetalAgent(TerrainAgent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model, "M")
