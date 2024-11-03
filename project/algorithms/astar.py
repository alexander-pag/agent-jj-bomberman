import heapq
from config.constants import HEURISTICS
from helpers.move_by_priority import get_neighbors_by_priority
import math


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

    from agents import RockAgent, MetalAgent, BorderAgent

    # Función para calcular la heurística (Manhattan o Euclidiana)
    def heuristic_manhattan_euclidean(a, b) -> int:
        if heuristic == HEURISTICS[0]:
            return abs(a[0] - b[0]) + abs(a[1] - b[1])
        return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    visited_order = []
    rocks_found = []  # Nueva lista para rocas
    g_score = {start: 0}
    f_score = {start: heuristic_manhattan_euclidean(start, goal)}

    while open_set:
        _, current = heapq.heappop(open_set)

        visited_order.append(current)

        if current == goal:
            # Reconstruir el camino
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            path.reverse()
            print(f"Path found: {path}")
            return path, visited_order, rocks_found

        # Obtener los vecinos ortogonales
        neighbors = model.grid.get_neighborhood(
            current, moore=False, include_center=False
        )
        # Obtener la prioridad desde el modelo (asegúrate de que esta propiedad existe)
        priority = model.priority
        # Ordenar los vecinos por prioridad
        ordered_neighbors = get_neighbors_by_priority(neighbors, current, priority)

        for neighbor in ordered_neighbors:
            # Asegurarse de que el vecino no esté fuera de límites
            if model.grid.out_of_bounds(neighbor):
                continue

            # Revisar si la celda está libre de obstáculos
            cell_contents = model.grid.get_cell_list_contents([neighbor])
            if any(isinstance(agent, (MetalAgent)) for agent in cell_contents):
                continue

            # Verificar si hay roca y registrarla
            if any(isinstance(agent, RockAgent) for agent in cell_contents):
                rocks_found.append(neighbor)
                # Continuamos, ya que podemos considerar esta ruta
                # sin bloquear el camino en sí
                continue

            if any(isinstance(agent, (BorderAgent)) for agent in cell_contents):
                continue

            tentative_g_score = g_score[current] + 1
            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + heuristic_manhattan_euclidean(
                    neighbor, goal
                )
                heapq.heappush(open_set, (f_score[neighbor], neighbor))

    return None, visited_order, rocks_found
