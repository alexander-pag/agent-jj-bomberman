from mesa import Agent
import logging
from agents.rockAgent import RockAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ExplosionAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.cooldown = 1

    def step(self):
        self.cooldown -= 1
        if self.cooldown <= 0:
            self.explode()

    def explode(self):
        """Realiza la explosión y elimina rocas en el área de efecto."""
        # Comprobar las posiciones a destruir (adjacentes)
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if abs(dx) + abs(dy) == 1:  # Solo posiciones adyacentes
                    explosion_position = (self.pos[0] + dx, self.pos[1] + dy)
                    agents_in_same_pos = self.model.grid.get_cell_list_contents(
                        [explosion_position]
                    )

                    # Verificar si hay un agente rock en la misma posición y eliminarlo
                    for agent in agents_in_same_pos:
                        if isinstance(agent, RockAgent):
                            self.model.grid.remove_agent(agent)
                            self.model.schedule.remove(agent)
                            logger.info(
                                f"Agente rock {agent.unique_id} eliminado por la explosión en {explosion_position}."
                            )

            # Remover la explosión del modelo y de la grilla
            self.model.grid.remove_agent(self)
            self.model.schedule.remove(self)
