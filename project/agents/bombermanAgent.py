from mesa import Agent
from algorithms import astar_search, bfs, ucs, dfs
from .metalAgent import MetalAgent
from .rockAgent import RockAgent
from config.constants import *
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BombermanAgent(Agent):
    def __init__(self, unique_id, model, start_pos):
        super().__init__(unique_id, model)
        self.pos = start_pos
        self.path = None
        self.goal = model.pos_goal
        self.algorithms = {
            DFS: dfs,
            UCS: ucs,
            BFS: bfs,
            ASTAR: astar_search,
        }

    def step(self) -> None:
        """Método que se ejecuta en cada paso del modelo."""
        if self.verify_exit():
            logger.info(
                f"Bomberman ha alcanzado la salida en {self.pos}. ¡Juego ganado!"
            )
            self.model.running = False  # Detener la simulación
            return

        # Intentar moverse en cada paso
        self.move()

    def verify_exit(self) -> bool:
        """Verifica si Bomberman ha alcanzado la salida."""
        return self.pos == self.goal

    def move(self) -> None:
        """Gestiona el movimiento del agente Bomberman."""
        if self.path is None or not self.path:
            self.calculate_path()

        if self.path:
            self.follow_path()

    def calculate_path(self) -> None:
        """Calcula el camino hacia la meta utilizando el algoritmo seleccionado."""
        logger.info(f"Calculando camino desde {self.pos} hasta {self.goal}")
        algorithm = self.algorithms.get(self.model.search_algorithm)

        if algorithm:
            if self.model.search_algorithm == ASTAR:
                self.path = algorithm(
                    self.pos, self.goal, self.model, self.model.heuristic
                )
            else:
                self.path = algorithm(self.pos, self.goal, self.model)

            if self.path is None:
                logger.warning(
                    f"No se encontró un camino desde {self.pos} hasta {self.goal}"
                )
            else:
                logger.info(f"Camino encontrado: {self.path}")
        else:
            logger.error(
                f"Algoritmo de búsqueda desconocido: {self.model.search_algorithm}"
            )

    def follow_path(self) -> None:
        """Sigue el camino calculado, moviéndose a la siguiente posición."""
        next_step = self.path.pop(0)

        if not self.verify_obstacle(
            self.model.grid.get_cell_list_contents([next_step])
        ):
            self.model.grid.move_agent(self, next_step)
            self.pos = next_step  # Actualizar la posición del agente
            self.model.visited_cells.add(self.pos)  # Registrar celda visitada
            logger.info(f"Movido a {self.pos}")

        if self.verify_exit():
            logger.info("¡Victoria! El Bomberman ha encontrado la salida.")
            self.model.running = False  # Detener la simulación

    def verify_obstacle(self, cellmates) -> bool:
        """
        Verifica si hay un agente de tipo obstáculo (Metal o Rock) en la celda.

        Args:
            cellmates: Lista de agentes en la celda.

        Returns:
            bool: True si hay un obstáculo, False en caso contrario.
        """
        for agent in cellmates:
            if isinstance(agent, (MetalAgent, RockAgent)):
                return True
        return False
