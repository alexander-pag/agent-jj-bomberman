import heapq
from agents import RockAgent, MetalAgent
from config.constants import HEURISTICS
import logging
import math

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def astar_search(start, goal, model, heuristic) -> list:
    """
    Implementación del algoritmo A* para encontrar el camino más corto entre dos puntos en un mapa.

    Args:
        start (tuple): Coordenadas de inicio.
        goal (tuple): Coordenadas de destino.
        model (BombermanModel): Instancia del modelo.
        heuristic (str): Nombre de la heurística a utilizar.

    Returns:
        list: Lista de coordenadas que representan el camino más corto entre start y goal.
    """

    # Movimiento en 4 direcciones (arriba, abajo, izquierda, derecha)
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]

    def heuristic_manhattan_euclidean(a, b) -> int:
        """
        Calcula la distancia de Manhattan entre dos puntos.

        Args:
            a (tuple): Coordenadas del punto A.
            b (tuple): Coordenadas del punto B.

        Returns:
            int: Distancia de Manhattan entre los dos puntos.
        """

        # Distancia de Manhattan
        if heuristic == HEURISTICS[0]:
            return abs(a[0] - b[0]) + abs(a[1] - b[1])

        # Distancia euclidiana
        return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic_manhattan_euclidean(start, goal)}

    logger.info(f"Starting A* from {start} to {goal}")

    while open_set:
        _, current = heapq.heappop(open_set)

        if current == goal:
            # Reconstruir el camino
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            path.reverse()
            print(f"Path found: {path}")
            return path

        logger.info(f"Processing current node: {current}")

        for direction in directions:
            neighbor = (current[0] + direction[0], current[1] + direction[1])

            # Asegurarse de que el vecino no esté fuera de límites
            if model.grid.out_of_bounds(neighbor):
                logger.info(f"Neighbor {neighbor} out of bounds")
                continue

            # Revisar si la celda está libre de obstáculos
            cell_contents = model.grid.get_cell_list_contents([neighbor])
            if any(isinstance(agent, (MetalAgent)) for agent in cell_contents):
                logger.info(f"Neighbor {neighbor} is an obstacle")
                continue

            if any(isinstance(agent, (RockAgent)) for agent in cell_contents):
                logger.info(f"Is rock {neighbor} break with dynamite")

            tentative_g_score = g_score[current] + 1
            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + heuristic_manhattan_euclidean(
                    neighbor, goal
                )
                heapq.heappush(open_set, (f_score[neighbor], neighbor))
                logger.info(
                    f"Neighbor {neighbor} added to open set with f_score {f_score[neighbor]}"
                )

    logger.warning(f"No path found from {start} to {goal}")
    return None  # No se encontró un camino
