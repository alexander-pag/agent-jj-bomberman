import heapq
import math
from config.constants import HEURISTICS

def manhattan_distance(pos1, pos2):
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

def euclidean_distance(pos1, pos2):
    return math.sqrt((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2)

def get_cost(agent, current_pos) -> float:
    from agents import GrassAgent, MetalAgent, BorderAgent

    if isinstance(agent, GrassAgent):
        return 10
    elif isinstance(agent, (MetalAgent, BorderAgent)):
        return float("inf")
    return 1

def beam_search(start_pos, goal_pos, model, heuristic_type, beam_width=4):
    if heuristic_type == HEURISTICS[0]:
        heuristic = manhattan_distance
    elif heuristic_type == HEURISTICS[1]:
        heuristic = euclidean_distance
    else:
        raise ValueError("Heurística desconocida. Usa 'manhattan' o 'euclidean'.")

    queue = [(heuristic(start_pos, goal_pos), start_pos, [start_pos])]
    visited = set()
    visited_order = []
    rocks_found = []  # Track rocks

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

            for neighbor in neighbors:
                if neighbor not in visited:
                    cellmates = model.grid.get_cell_list_contents([neighbor])
                    from agents import RockAgent
                    # Check for rocks
                    if any(isinstance(agent, RockAgent) for agent in cellmates):
                        if neighbor not in rocks_found:
                            rocks_found.append(neighbor)
                    
                    # Only block for metal/border
                    from agents import MetalAgent, BorderAgent
                    if not any(isinstance(agent, (MetalAgent, BorderAgent)) for agent in cellmates):
                        h = heuristic(neighbor, goal_pos)
                        heapq.heappush(next_level, (h, neighbor, path + [neighbor]))

        queue = next_level

    return None, visited_order, rocks_found