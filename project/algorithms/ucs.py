import heapq
import logging
from helpers.move_by_priority import get_neighbors_by_priority

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_cost(agent, current_pos, rocks) -> float:
    """
    Determina el costo de moverse a una celda en función del tipo de agente.

    Args:
        agent: Agente que ocupa la celda.
        current_pos: Tupla que representa la posición actual.

    Returns:
        float: Costo de moverse a la celda.
    """

    from agents import GrassAgent, RockAgent, MetalAgent, BorderAgent, GoalAgent

    if isinstance(agent, GrassAgent) or isinstance(agent, GoalAgent):
        if agent.pos[1] > current_pos[1]:
            return 10, rocks
        elif agent.pos[1] < current_pos[1]:
            return 10, rocks
        elif agent.pos[0] > current_pos[0]:
            return 10, rocks
        elif agent.pos[0] < current_pos[0]:
            return 10, rocks
    elif isinstance(agent, RockAgent):
        return 20, rocks + [agent.pos]
    elif isinstance(agent, MetalAgent) or isinstance(agent, BorderAgent):
        return float("inf"), rocks
    return 1, rocks  # Costo por defecto


def ucs(start_pos, goal_pos, model) -> list:
    """
    Implementa el algoritmo de búsqueda con costo uniforme (UCS) para encontrar un camino
    desde una posición inicial hasta una posición objetivo en un modelo de grid.

    Args:
        start_pos: Tupla que representa la posición inicial.
        goal_pos: Tupla que representa la posición objetivo.
        model: Modelo del entorno que contiene la información del grid y los agentes.

    Returns:
        Una lista de posiciones que representa el camino encontrado, o None si no existe camino.
    """
    # Cola de prioridad para almacenar (costo acumulado, contador de desempate, posición actual, camino)
    queue = []
    counter = 0  # Contador para desempatar en caso de igual costo
    heapq.heappush(
        queue, (0, counter, start_pos, [start_pos])
    )  # Inicialmente añadimos el nodo de inicio
    visited = set()  # Conjunto de nodos visitados
    visited_order = []
    cost_so_far = {start_pos: 0}  # Costo acumulado hasta la celda
    priority = model.priority  # Obtén la prioridad de la exploración desde el modelo
    rocks_found = []  # Lista de rocas encontradas

    while queue:
        # Sacar el nodo con el menor costo acumulado
        current_cost, _, current_pos, path = heapq.heappop(queue)

        if current_pos in visited:
            continue  # Saltamos si ya fue visitado

        visited.add(current_pos)
        visited_order.append(current_pos)

        # Si llegamos a la meta, devolvemos el camino
        if current_pos == goal_pos:
            return path, visited_order, rocks_found

        # Obtener las celdas vecinas ortogonalmente
        neighbors = model.grid.get_neighborhood(
            current_pos, moore=False, include_center=False
        )

        # Ordenar los vecinos según la prioridad (como cadena)
        ordered_neighbors = get_neighbors_by_priority(neighbors, current_pos, priority)

        for neighbor in ordered_neighbors:
            if neighbor not in visited:
                cellmates = model.grid.get_cell_list_contents([neighbor])

                # Inicializa el costo de movimiento y la lista de rocas locales
                move_cost = 0
                rocks = rocks_found.copy()

                for agent in cellmates:
                    cost, rocks = get_cost(agent, current_pos, rocks)
                    move_cost += cost

                # Si el costo es menor que infinito, significa que la celda es transitable
                if move_cost < float("inf"):
                    new_cost = current_cost + move_cost
                    if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                        cost_so_far[neighbor] = new_cost
                        counter += 1
                        rocks_found = (
                            rocks  # Actualiza la lista global de rocas encontradas
                        )
                        heapq.heappush(
                            queue, (new_cost, counter, neighbor, path + [neighbor])
                        )

    return None, visited_order, rocks  # Si no se encuentra un camino
