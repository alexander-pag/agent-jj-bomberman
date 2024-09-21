import os
from PIL import Image
from functools import lru_cache


# Función para cargar el mapa desde un archivo de texto
def read_map_from_file(filename) -> list:
    """
    Lee un archivo de texto y devuelve una lista de listas con los datos del mapa.

    Args:
        filename (str): Nombre del archivo a leer.
    """
    with open(filename, "r") as f:
        map_data = [line.strip().split(", ") for line in f]
    return map_data


def load_image(image_path, sprite_width, sprite_height, pos=0) -> str:
    """
    Carga una imagen y recorta un sprite de ella, almacenándolo en un nuevo archivo.

    Args:
        image_path (str): Ruta de la imagen a cargar.
        sprite_width (int): Ancho del sprite a recortar.
        sprite_height (int): Alto del sprite a recortar.
        pos (int): Posición del sprite en la imagen.
    """
    # Cargar la imagen solo si no está en caché
    image = Image.open(image_path)
    sprite = image.crop(
        (pos * sprite_width, 0, (pos + 1) * sprite_width, sprite_height)
    )
    sprite_filename = f"sprite_{os.path.basename(image_path)}"
    sprite.save(sprite_filename)

    # Devolver el nombre del archivo con el sprite
    return sprite_filename


@lru_cache(maxsize=None)
def get_image_path(image_path):
    return image_path
