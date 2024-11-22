import numpy as np


def map_to_matrix(map_data):
    """
    Convierte una lista de listas con los datos de un mapa en una matriz de numpy.

    Args:
        map_data (list): Lista de listas con los datos del mapa.

    Returns:
        numpy.ndarray: Matriz con los datos del mapa.
    """
    # Girar el mapa 180 grados
    map_data = map_data[::-1]
    return np.array(map_data)
