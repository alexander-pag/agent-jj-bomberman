__package__ = "agents"

from mesa import Agent
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ExplosionAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.duration = 1  # Duración de la explosión en pasos

    def step(self):
        self.duration -= 1
        if self.duration <= 0:
            self.model.schedule.remove(self)
            self.model.grid.remove_agent(self)
