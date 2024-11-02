import heapq
import math
from config.constants import HEURISTICS


def manhattan_distance(pos1, pos2):
    """Calcula la distancia Manhattan entre dos posiciones en un grid."""
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])


def euclidean_distance(pos1, pos2):
    """Calcula la distancia Euclidiana entre dos posiciones en un grid."""
    return math.sqrt((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2)


def get_cost(agent, current_pos) -> float:
    """
    Determina el costo de moverse a una celda en función del tipo de agente.
    """
    from agents import GrassAgent, RockAgent, MetalAgent, BorderAgent

    if isinstance(agent, GrassAgent):
        return 10
    elif isinstance(agent, (RockAgent, MetalAgent, BorderAgent)):
        return float("inf")
    return 1  # Costo por defecto


def beam_search(start_pos, goal_pos, model, heuristic_type, beam_width=4):
    """
    Algoritmo Beam Search que encuentra el camino desde start_pos hasta goal_pos en un grid usando un beam width.

    Args:
        start_pos: Tupla con la posición de inicio.
        goal_pos: Tupla con la posición objetivo.
        model: Modelo del entorno que contiene el grid y los agentes.
        heuristic_type: 'manhattan' o 'euclidean' para definir el tipo de heurística.
        beam_width: Número de nodos a expandir en cada nivel (ancho del haz).

    Returns:
        Una lista de posiciones que representa el camino encontrado, o None si no se encuentra camino.
    """
    # Función heurística (dependiendo del tipo especificado)
    if heuristic_type == HEURISTICS[0]:
        heuristic = manhattan_distance
    elif heuristic_type == HEURISTICS[1]:
        heuristic = euclidean_distance
    else:
        raise ValueError("Heurística desconocida. Usa 'manhattan' o 'euclidean'.")

    # Cola de prioridad para almacenar (heurística, posición actual, camino)
    queue = [(heuristic(start_pos, goal_pos), start_pos, [start_pos])]
    visited = set()  # Conjunto de nodos visitados
    visited_order = []

    while queue:
        # Sólo expandimos los mejores `beam_width` nodos en cada nivel
        next_level = []

        for _ in range(min(beam_width, len(queue))):
            _, current_pos, path = heapq.heappop(queue)

            visited_order.append(current_pos)

            # Si llegamos a la meta, devolvemos el camino
            if current_pos == goal_pos:
                return path, visited_order

            # Si el nodo ya fue visitado, saltamos
            if current_pos in visited:
                continue

            visited.add(current_pos)

            # Obtener las celdas vecinas
            neighbors = model.grid.get_neighborhood(
                current_pos, moore=False, include_center=False
            )

            # Filtrar vecinos no visitados y calcular costos
            for neighbor in neighbors:
                if neighbor not in visited:
                    cellmates = model.grid.get_cell_list_contents([neighbor])
                    move_cost = sum(get_cost(agent, current_pos) for agent in cellmates)

                    if move_cost < float("inf"):
                        # Calcular heurística y añadir a la cola de la siguiente expansión
                        h = heuristic(neighbor, goal_pos)
                        heapq.heappush(next_level, (h, neighbor, path + [neighbor]))

        # Reemplazar la cola actual con los mejores nodos para el siguiente nivel
        queue = next_level

    # Si no encontramos camino
    return None, visited_order
