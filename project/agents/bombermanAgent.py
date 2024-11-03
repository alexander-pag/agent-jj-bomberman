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
        algorithm = self.algorithms.get(self.model.search_algorithm)

        if algorithm:
            if self.model.search_algorithm in [ASTAR, BEAM, HILL]:
                self.path, visited_order = algorithm(
                    self.pos,
                    self.goal,
                    self.model,
                    self.model.heuristic,
                )
            else:
                self.path, visited_order, rocks = algorithm(self.pos, self.goal, self.model)

            logger.info(f"Posición actual: {self.pos}")
            logger.info(f"Posición objetivo: {self.goal}")
            logger.info(f"Posiciones visitadas: {visited_order}")
            
            if rocks:
                rock_pos = rocks[0]
                logger.info(f"Roca detectada en: {rock_pos}")
                
                # Verificar si ya estamos adyacentes a la roca
                if self.is_adjacent(self.pos, rock_pos):
                    logger.info(f"Adyacente a roca en {rock_pos}, detonando bomba")
                    self.model.throw_bomb(self.pos, rock_pos)
                    return self.calculate_path()
                
                # Si no estamos adyacentes, calcular camino hacia la roca
                path_to_rock, _, _ = algorithm(self.pos, rock_pos, self.model)
                if path_to_rock:
                    logger.info(f"Camino hacia la roca: {path_to_rock}")
                    self.path = path_to_rock[:-1]
                    return
                
            else:
                if self.path:
                    self.model.visited_cells = [
                        (pos, idx + 1) for idx, pos in enumerate(visited_order)
                    ]
                    self.model.final_path_cells = set(self.path)
                else:
                    logger.error("No se encontró camino y no hay rocas para destruir")
                    return None

    def is_adjacent(self, pos1, pos2):
        """Verifica si dos posiciones son adyacentes"""
        x1, y1 = pos1
        x2, y2 = pos2
        return abs(x1 - x2) + abs(y1 - y2) == 1

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
