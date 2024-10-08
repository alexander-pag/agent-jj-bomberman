__package__ = "agents"
from .terrainAgent import TerrainAgent


class BorderAgent(TerrainAgent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model, "X")
