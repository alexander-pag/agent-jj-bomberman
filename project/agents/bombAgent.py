from mesa import Agent
from agents.borderAgent import BorderAgent
from agents.explosionAgent import ExplosionAgent
from agents.grassAgent import GrassAgent
from agents.metalAgent import MetalAgent
from agents.rockAgent import RockAgent
import logging
from collections import deque

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BombAgent(Agent):
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model)
        self.power = model.destruction_power
        self.cooldown = 1 + self.power
        self.pos = pos

    def step(self):
        # Reducir el tiempo de enfriamiento en cada paso
        self.cooldown -= 1
        if self.cooldown <= 0:
            self.explode()  # Explota cuando el tiempo llega a 0
            self.model.schedule.remove(self)
            self.model.grid.remove_agent(self)

    def explode(self):
        # Crear lista para rastrear cambios
        changes = []

        # Agregar explosión en la posición donde se plantó la bomba
        explosion = ExplosionAgent(self.model.next_id(), self.model)
        changes.append(("add_explosion", explosion, self.pos))

        # Direcciones ortogonales
        directions = [
            (1, 0),  # Abajo
            (-1, 0),  # Arriba
            (0, 1),  # Derecha
            (0, -1),  # Izquierda
        ]

        # Explorar en cada dirección
        for dx, dy in directions:
            current_pos = self.pos
            for step in range(1, self.power + 1):
                # Calcular la nueva posición
                next_pos = (current_pos[0] + dx, current_pos[1] + dy)

                # Verificar límites de la cuadrícula
                if not (
                    0 <= next_pos[0] < self.model.grid.width
                    and 0 <= next_pos[1] < self.model.grid.height
                ):
                    break

                # Obtener agentes en la celda actual
                cell_contents = self.model.grid.get_cell_list_contents(next_pos)

                # Detener propagación si hay un obstáculo (Metal o Border)
                if any(
                    isinstance(agent, (MetalAgent, BorderAgent))
                    for agent in cell_contents
                ):
                    break

                # Manejar rocas
                if any(isinstance(agent, RockAgent) for agent in cell_contents):
                    for agent in cell_contents:
                        if isinstance(agent, RockAgent):
                            changes.append(("remove", agent, next_pos))
                            grass = GrassAgent(self.model.next_id(), self.model)
                            changes.append(("add_grass", grass, next_pos))

                    # Agregar explosión en la posición de la roca destruida
                    explosion = ExplosionAgent(self.model.next_id(), self.model)
                    changes.append(("add_explosion", explosion, next_pos))

                    break  # Detener propagación en esta dirección después de destruir la roca

                # Agregar explosión en la posición actual
                explosion = ExplosionAgent(self.model.next_id(), self.model)
                changes.append(("add_explosion", explosion, next_pos))

                # Actualizar la posición actual
                current_pos = next_pos

        # Aplicar cambios de forma atómica
        for action, agent, pos in changes:
            if action == "remove":
                self.model.grid.remove_agent(agent)
                self.model.schedule.remove(agent)
            elif action in ["add_explosion", "add_grass"]:
                self.model.grid.place_agent(agent, pos)
                self.model.schedule.add(agent)
