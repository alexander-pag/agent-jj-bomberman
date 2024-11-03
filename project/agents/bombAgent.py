from mesa import Agent
from agents.explosionAgent import ExplosionAgent
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BombAgent(Agent):
    def __init__(self, unique_id, model, pd, pos):
        super().__init__(unique_id, model)
        self.pos = pos
        self.pd = pd
        self.cooldown = pd + 1
        self.exploded = False  # Inicializar el atributo de explosión

    def step(self):
        self.cooldown -= 1
        if self.cooldown <= 0 and not self.exploded:
            self.trigger_explosion()

    def trigger_explosion(self):
        """Trigger the explosion effect."""
        explosion_agent = ExplosionAgent(
            self.model.schedule.get_agent_count(), self.model
        )
        self.model.schedule.add(explosion_agent)
        self.model.grid.place_agent(explosion_agent, self.pos)
        self.exploded = True  # Cambiar el estado de la bomba a explotada
        logger.info(f"Bomba en {self.pos} ha explotado.")
