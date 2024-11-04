import heapq
import logging
from helpers.move_by_priority import get_neighbors_by_priority

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_cost(agent, current_pos, rocks) -> tuple:
    """
    Determina el costo de moverse a una celda según el tipo de agente.
    
    Args:
        agent: Agente que ocupa la celda
        current_pos: Posición actual desde donde se mueve
        rocks: Lista de rocas encontradas hasta el momento
        
    Returns:
        tuple: (costo del movimiento, lista actualizada de rocas)
    """
    from agents import GrassAgent, RockAgent, MetalAgent, BorderAgent, GoalAgent

    if isinstance(agent, (GrassAgent, GoalAgent)):
        # Mayor costo para movimientos verticales/horizontales
        if agent.pos[1] != current_pos[1] or agent.pos[0] != current_pos[0]:
            return 10, rocks
        return 1, rocks
        
    elif isinstance(agent, RockAgent):
        if agent.pos not in rocks:
            rocks.append(agent.pos)
        return 20, rocks
        
    elif isinstance(agent, (MetalAgent, BorderAgent)):
        return float("inf"), rocks
        
    return 1, rocks  # Costo base por defecto

def calculate_path_cost(path, rocks_in_path):
    """Calculate total cost including rock breaking."""
    ROCK_BREAK_COST = 3
    basic_cost = len(path) if path else float('inf')
    rock_cost = len(rocks_in_path) * ROCK_BREAK_COST
    return basic_cost + rock_cost

def ucs(start, goal, model) -> tuple:
    """UCS implementation comparing paths with and without rocks."""
    # Find both paths
    path_with_rocks = find_path(start, goal, model, allow_rocks=True)
    path_without_rocks = find_path(start, goal, model, allow_rocks=False)
    
    # Calculate costs
    rocks_in_path = []
    if path_with_rocks[0]:
        rocks_in_path = path_with_rocks[2]  # Get rocks found during search
    
    cost_with_rocks = calculate_path_cost(path_with_rocks[0], rocks_in_path)
    cost_without_rocks = calculate_path_cost(path_without_rocks[0], [])
    
    print("\nComparación de costos:")
    print(f"Camino con rocas: {cost_with_rocks} pasos (básico: {len(path_with_rocks[0]) if path_with_rocks[0] else 'inf'}, rocas: {len(rocks_in_path)})")
    print(f"Camino sin rocas: {cost_without_rocks} pasos")
    print(f"Eligiendo camino {'con' if cost_with_rocks < cost_without_rocks else 'sin'} rocas\n")
    
    # Return optimal path
    if cost_with_rocks < cost_without_rocks:
        return path_with_rocks
    return path_without_rocks

def find_path(start_pos, goal_pos, model, allow_rocks=False):
    """Helper function to find path with UCS."""
    queue = []
    counter = 0
    heapq.heappush(queue, (0, counter, start_pos, [start_pos]))
    visited = set()
    visited_order = []
    cost_so_far = {start_pos: 0}
    rocks_found = []

    while queue:
        current_cost, _, current_pos, path = heapq.heappop(queue)

        if current_pos in visited:
            continue

        visited.add(current_pos)
        visited_order.append(current_pos)

        if current_pos == goal_pos:
            return path, visited_order, rocks_found

        neighbors = model.grid.get_neighborhood(
            current_pos, moore=False, include_center=False
        )
        ordered_neighbors = get_neighbors_by_priority(neighbors, current_pos, model.priority)
        from agents import RockAgent
        for neighbor in ordered_neighbors:
            if neighbor not in visited:
                cellmates = model.grid.get_cell_list_contents([neighbor])
                move_cost = 0
                rocks = rocks_found.copy()

                for agent in cellmates:
                    if not allow_rocks and isinstance(agent, RockAgent):
                        move_cost = float("inf")
                        break
                    
                    cost, rocks = get_cost(agent, current_pos, rocks)
                    move_cost += cost

                if move_cost < float("inf"):
                    new_cost = current_cost + move_cost
                    if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                        cost_so_far[neighbor] = new_cost
                        counter += 1
                        rocks_found = rocks
                        heapq.heappush(queue, (new_cost, counter, neighbor, path + [neighbor]))

    return None, visited_order, rocks_found
