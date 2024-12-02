from mesa.time import BaseScheduler
from agents import BombermanAgent

class CustomScheduler(BaseScheduler):
    def step(self):
        """
        Realiza un paso del modelo activando los agentes en un orden específico.
        El Bomberman se activa primero, seguido por el resto de los agentes.
        """
        # Activar primero el agente Bomberman
        for agent in self.agents:
            if isinstance(agent, BombermanAgent):
                agent.step()

        # Activar el resto de los agentes
        for agent in self.agents:
            if not isinstance(agent, BombermanAgent):
                agent.step()

        self.steps += 1
        self.time += 1
