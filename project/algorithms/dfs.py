import logging
from helpers.move_by_priority import get_neighbors_by_priority

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def calculate_path_cost(path, rocks_in_path):
    """Calculate total cost of path including rock breaking."""
    ROCK_BREAK_COST = 3  # Cost of placing bomb + retreat + recalculate
    basic_cost = len(path) if path else float('inf')
    rock_cost = len(rocks_in_path) * ROCK_BREAK_COST
    return basic_cost + rock_cost

def dfs(start, goal, model) -> tuple:
    """DFS implementation comparing paths with and without rocks."""
    # Find both paths
    path_with_rocks = find_path(start, goal, model, allow_rocks=True)
    path_without_rocks = find_path(start, goal, model, allow_rocks=False)
    from agents import RockAgent
    # Calculate costs
    rocks_in_path = []
    if path_with_rocks[0]:
        rocks_in_path = [pos for pos in path_with_rocks[0] if 
                        any(isinstance(agent, RockAgent) 
                            for agent in model.grid.get_cell_list_contents([pos]))]
    
    cost_with_rocks = calculate_path_cost(path_with_rocks[0], rocks_in_path)
    cost_without_rocks = calculate_path_cost(path_without_rocks[0], [])
    
    print("\nComparación de costos:")
    print(f"Camino con rocas: {cost_with_rocks} pasos (básico: {len(path_with_rocks[0]) if path_with_rocks[0] else 'inf'}, rocas: {len(rocks_in_path)})")
    print(f"Camino sin rocas: {cost_without_rocks} pasos")
    print(f"Eligiendo camino {'con' if cost_with_rocks < cost_without_rocks else 'sin'} rocas\n")
    
    # Return optimal path
    if cost_with_rocks < cost_without_rocks:
        return path_with_rocks[0], path_with_rocks[1], rocks_in_path
    return path_without_rocks[0], path_without_rocks[1], []

def find_path(start, goal, model, allow_rocks=False):
    """Helper function to find path with DFS."""
    stack = [(start, [start])]
    visited = set()
    visited_order = []
    rocks_found = []

    def is_valid_move(pos):
        from agents import RockAgent, MetalAgent, BorderAgent

        if model.grid.out_of_bounds(pos):
            return False
            
        cell_contents = model.grid.get_cell_list_contents([pos])
        if any(isinstance(agent, (MetalAgent, BorderAgent)) for agent in cell_contents):
            return False
            
        if not allow_rocks and any(isinstance(agent, RockAgent) for agent in cell_contents):
            return False
            
        return True

    while stack:
        current, path = stack.pop()
        visited_order.append(current)

        if current == goal:
            return path, visited_order

        if current not in visited:
            visited.add(current)
            neighbors = model.grid.get_neighborhood(
                current, moore=False, include_center=False
            )
            ordered_neighbors = get_neighbors_by_priority(neighbors, current, model.priority)

            for neighbor in reversed(ordered_neighbors):
                if is_valid_move(neighbor) and neighbor not in visited:
                    stack.append((neighbor, path + [neighbor]))

    return None, visited_order