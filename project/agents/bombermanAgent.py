from mesa import Agent
from algorithms import astar_search, bfs, ucs, dfs, beam_search, hill_climbing
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
            BEAM: beam_search,
            HILL: hill_climbing,
        }

    def step(self) -> None:
        """Método que se ejecuta en cada paso del modelo."""
        if self.verify_exit():
            self.model.running = False
            return

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
        algorithm = self.algorithms.get(self.model.search_algorithm)

        logger.info(
            f"Ejecutando juego con: {self.model.search_algorithm} y prioridad: {self.model.priority}. {self.model.heuristic}"
        )

        if algorithm:
            if (
                self.model.search_algorithm == ASTAR
                or self.model.search_algorithm == BEAM
                or self.model.search_algorithm == HILL
            ):
                self.path, visited_order = algorithm(
                    self.pos,
                    self.goal,
                    self.model,
                    self.model.heuristic,
                )
            else:
                self.path, visited_order = algorithm(self.pos, self.goal, self.model)

            if self.path is None:
                logger.warning(
                    f"No se encontró un camino desde {self.pos} hasta {self.goal}"
                )
            else:
                # Guardar el orden en que se visitaron los nodos
                self.model.visited_cells = [
                    (pos, idx + 1) for idx, pos in enumerate(visited_order)
                ]

                # Guardar las celdas que son parte del camino final
                self.model.final_path_cells = set(self.path)
        else:
            logger.error(
                f"Algoritmo de búsqueda desconocido: {self.model.search_algorithm}"
            )

    def follow_path(self) -> None:
        """Sigue el camino calculado, moviéndose a la siguiente posición."""
        if self.path:
            next_step = self.path.pop(0)

            self.model.grid.move_agent(self, next_step)
            self.pos = next_step

            if self.pos not in [pos for pos, _ in self.model.visited_cells]:
                visit_number = len(self.model.visited_cells) + 1
                self.model.visited_cells.append((self.pos, visit_number))

            if self.pos not in self.model.visited_ground_cells:
                self.model.visited_ground_cells.add(self.pos)

        if self.verify_exit():
            self.model.running = False
