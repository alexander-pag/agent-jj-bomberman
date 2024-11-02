from helpers.file_reader import read_map_from_file
from config.constants import BOMBERMAN, GOAL


def load_map_from_file(file_path):
    map_data = read_map_from_file(file_path)

    # Invertir el mapa
    map_data = map_data[::-1]

    pos_bomberman, pos_goal = get_special_positions(map_data)
    width = len(map_data[0])
    height = len(map_data)
    return map_data, pos_bomberman, pos_goal, width, height


def get_special_positions(map_data) -> tuple:
    """
    Obtiene las posiciones de Bomberman y la salida del mapa.

    Args:
        map_data: Lista de listas que representa el mapa.

    Returns:
        Tupla con las posiciones de Bomberman y la salida
    """
    pos_bomberman = None
    pos_goal = None
    for y, row in enumerate(map_data):
        for x, cell in enumerate(row):
            if cell == BOMBERMAN:
                pos_bomberman = (x, y)
            elif cell == GOAL:
                pos_goal = (x, y)
    return pos_bomberman, pos_goal
