import heapq
import math
from config.constants import HEURISTICS
from helpers.move_by_priority import get_neighbors_by_priority


def manhattan_distance(pos1, pos2):
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

def euclidean_distance(pos1, pos2):
    return math.sqrt((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2)

def calculate_path_cost(path, rocks_in_path):
    """Calculate total cost including rock breaking."""
    ROCK_BREAK_COST = 3
    basic_cost = len(path) if path else float('inf')
    rock_cost = len(rocks_in_path) * ROCK_BREAK_COST
    return basic_cost + rock_cost

def beam_search(start_pos, goal_pos, model, heuristic_type, beam_width=4):
    """Beam search comparing paths with and without rocks."""
    # Find both paths
    path_with_rocks = find_path(start_pos, goal_pos, model, heuristic_type, beam_width, allow_rocks=True)
    path_without_rocks = find_path(start_pos, goal_pos, model, heuristic_type, beam_width, allow_rocks=False)
    
    # Calculate costs
    rocks_in_path = []
    if path_with_rocks[0]:
        rocks_in_path = path_with_rocks[2]
    
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

def find_path(start_pos, goal_pos, model, heuristic_type, beam_width=4, allow_rocks=False):
    """Helper function to find path with beam search."""
    if heuristic_type == HEURISTICS[0]:
        heuristic = manhattan_distance
    else:
        heuristic = euclidean_distance

    queue = [(heuristic(start_pos, goal_pos), start_pos, [start_pos])]
    visited = set()
    visited_order = []
    rocks_found = []

    while queue:
        next_level = []

        for _ in range(min(beam_width, len(queue))):
            _, current_pos, path = heapq.heappop(queue)
            visited_order.append(current_pos)

            if current_pos == goal_pos:
                return path, visited_order, rocks_found

            if current_pos in visited:
                continue

            visited.add(current_pos)

            neighbors = model.grid.get_neighborhood(
                current_pos, moore=False, include_center=False
            )
            ordered_neighbors = get_neighbors_by_priority(neighbors, current_pos, model.priority)
            from agents import RockAgent, MetalAgent, BorderAgent
            for neighbor in ordered_neighbors:
                if neighbor not in visited:
                    cellmates = model.grid.get_cell_list_contents([neighbor])
                    
                    # Check for rocks
                    if any(isinstance(agent, RockAgent) for agent in cellmates):
                        if neighbor not in rocks_found:
                            rocks_found.append(neighbor)
                            if not allow_rocks:
                                continue
                    
                    # Only block for metal/border
                    if not any(isinstance(agent, (MetalAgent, BorderAgent)) for agent in cellmates):
                        h = heuristic(neighbor, goal_pos)
                        heapq.heappush(next_level, (h, neighbor, path + [neighbor]))

        queue = next_level

    return None, visited_order, rocks_found