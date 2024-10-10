from .terrainAgent import TerrainAgent


class GoalAgent(TerrainAgent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model, "G")
