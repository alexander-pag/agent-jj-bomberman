import heapq
from agents import GrassAgent, RockAgent, MetalAgent
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_cost(agent, current_pos) -> float:
    """
    Determina el costo de moverse a una celda en función del tipo de agente.

    Args:
        agent: Agente que ocupa la celda.
        current_pos: Tupla que representa la posición actual.

    Returns:
        float: Costo de moverse a la celda.
    """
    if isinstance(agent, GrassAgent):
        if agent.pos[1] > current_pos[1]:
            return 1.3  # Costo para el caso en que el movimiento sea en el eje Y hacia arriba
        elif agent.pos[1] < current_pos[1]:
            return (
                3  # Costo para el caso en que el movimiento sea en el eje Y hacia abajo
            )
        elif agent.pos[0] > current_pos[0]:
            return 4  # Costo para el caso en que el movimiento sea en el eje X hacia la derecha
        elif agent.pos[0] < current_pos[0]:
            return 2  # Costo para el caso en que el movimiento sea en el eje X hacia la izquierda
    elif isinstance(agent, RockAgent) or isinstance(agent, MetalAgent):
        return float("inf")  # Imposible moverse a una celda con roca o metal
    return 1  # Costo por defecto si no hay agentes de terreno (quizás terreno vacío)


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
    # Cola de prioridad para almacenar (costo acumulado, posición actual, camino)
    queue = [(0, start_pos, [start_pos])]
    # El heap se inicializa con el nodo inicial (costo 0, posición inicial, camino inicial)

    visited = set()  # Conjunto de nodos visitados
    cost_so_far = {start_pos: 0}  # Costo acumulado hasta la celda

    while queue:
        # Sacar el nodo con el menor costo acumulado
        current_cost, current_pos, path = heapq.heappop(queue)
        logger.info(f"Explorando {current_pos} con costo {current_cost}")
        logger.info(f"Camino actual: {path}")
        logger.info(f"Costo acumulado: {cost_so_far[current_pos]}")
        logger.info(f"Cola de prioridad: {queue}")
        logger.info(f"Nodos visitados: {visited}")

        if current_pos in visited:
            continue  # Saltamos si ya fue visitado

        visited.add(current_pos)

        # Si llegamos a la meta, devolvemos el camino
        if current_pos == goal_pos:
            return path

        # Obtener las celdas vecinas ortogonalmente
        neighbors = model.grid.get_neighborhood(
            current_pos, moore=False, include_center=False
        )

        for neighbor in neighbors:
            if neighbor not in visited:
                # Obtener el contenido de la celda vecina
                cellmates = model.grid.get_cell_list_contents([neighbor])
                # Asignar el costo de la celda según el tipo de terreno
                move_cost = sum(get_cost(agent, current_pos) for agent in cellmates)

                # Si la celda es transitable (sin obstáculos insalvables)
                if move_cost < float("inf"):
                    new_cost = current_cost + move_cost
                    if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                        cost_so_far[neighbor] = new_cost
                        priority = new_cost
                        heapq.heappush(queue, (priority, neighbor, path + [neighbor]))

    return None  # Si no se encuentra un camino
