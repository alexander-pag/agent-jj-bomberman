import math


def manhattan_distance(pos1, pos2):
    """Calcula la distancia Manhattan entre dos posiciones en un grid."""
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])


def euclidean_distance(pos1, pos2):
    """Calcula la distancia Euclidiana entre dos posiciones en un grid."""
    return math.sqrt((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2)


def calculate_path_cost(path, rocks_in_path):
    """Calculate total cost including rock breaking."""
    ROCK_BREAK_COST = 3
    basic_cost = len(path) if path else float("inf")
    rock_cost = len(rocks_in_path) * ROCK_BREAK_COST
    return basic_cost + rock_cost
