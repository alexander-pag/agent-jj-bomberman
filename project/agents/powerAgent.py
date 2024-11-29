from mesa import Agent

class PowerAgent(Agent):
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model)
        self.pos = pos

    def step(self) -> None:
        """Realiza un paso en la simulación."""
        pass