import heapq
from config.constants import HEURISTICS
from helpers.move_by_priority import get_neighbors_by_priority
import math


def calculate_path_cost(path, rocks_in_path):
    """Calculate total cost of path including rock breaking."""
    ROCK_BREAK_COST = 3  # Cost of placing bomb + retreat + recalculate
    basic_cost = len(path) if path else float('inf')
    rock_cost = len(rocks_in_path) * ROCK_BREAK_COST
    return basic_cost + rock_cost

def astar_search(start, goal, model, heuristic) -> tuple:
    """A* search comparing paths with and without rocks."""
    # Find both paths
    path_with_rocks = find_path(start, goal, model, heuristic, allow_rocks=True)
    path_without_rocks = find_path(start, goal, model, heuristic, allow_rocks=False)
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

def find_path(start, goal, model, heuristic, allow_rocks=False):
    """Helper function to find path with A*."""
    from agents import RockAgent, MetalAgent, BorderAgent

    def heuristic_manhattan_euclidean(a, b) -> float:
        if heuristic == HEURISTICS[0]:
            return abs(a[0] - b[0]) + abs(a[1] - b[1])
        return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    visited_order = []
    g_score = {start: 0}
    f_score = {start: heuristic_manhattan_euclidean(start, goal)}

    while open_set:
        _, current = heapq.heappop(open_set)
        visited_order.append(current)

        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            path.reverse()
            return path, visited_order

        neighbors = model.grid.get_neighborhood(current, moore=False, include_center=False)
        ordered_neighbors = get_neighbors_by_priority(neighbors, current, model.priority)

        for neighbor in ordered_neighbors:
            if model.grid.out_of_bounds(neighbor):
                continue

            cell_contents = model.grid.get_cell_list_contents([neighbor])
            if any(isinstance(agent, (MetalAgent, BorderAgent)) for agent in cell_contents):
                continue
                
            if not allow_rocks and any(isinstance(agent, RockAgent) for agent in cell_contents):
                continue

            tentative_g_score = g_score[current] + 1
            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + heuristic_manhattan_euclidean(neighbor, goal)
                heapq.heappush(open_set, (f_score[neighbor], neighbor))

    return None, visited_order
