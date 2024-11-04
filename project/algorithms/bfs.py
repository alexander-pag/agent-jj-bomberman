from collections import deque
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

def bfs(start_pos, goal_pos, model):
    """BFS implementation that compares paths with and without rocks."""
    # Path allowing rocks
    path_with_rocks = find_path(start_pos, goal_pos, model, allow_rocks=True)
    # Path avoiding rocks
    path_without_rocks = find_path(start_pos, goal_pos, model, allow_rocks=False)
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

def find_path(start_pos, goal_pos, model, allow_rocks=False):
    """Helper function to find path with or without allowing rocks."""
    queue = deque([(start_pos, [start_pos])])
    visited = {start_pos}
    visited_order = []

    while queue:
        current_pos, path = queue.popleft()
        visited_order.append(current_pos)

        if current_pos == goal_pos:
            return path, visited_order

        neighbors = model.grid.get_neighborhood(
            current_pos, moore=False, include_center=False
        )
        ordered_neighbors = get_neighbors_by_priority(neighbors, current_pos, model.priority)
        from agents import RockAgent, MetalAgent, BorderAgent

        for next_pos in ordered_neighbors:
            if next_pos not in visited:
                cell_contents = model.grid.get_cell_list_contents([next_pos])
                
                # Check for obstacles
                if any(isinstance(agent, (MetalAgent, BorderAgent)) for agent in cell_contents):
                    continue
                
                # Handle rocks based on allow_rocks parameter
                if not allow_rocks and any(isinstance(agent, RockAgent) for agent in cell_contents):
                    continue

                visited.add(next_pos)
                queue.append((next_pos, path + [next_pos]))

    return None, visited_order