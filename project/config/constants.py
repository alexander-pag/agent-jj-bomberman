# Nombres de los agentes
BOMBERMAN_AGENT = "Bomberman"
GRASS_AGENT = "Grass"
ROCK_AGENT = "Rock"
METAL_AGENT = "Metal"

# Dimensiones por defecto del grid
DEFAULT_GRID_WIDTH = 600
DEFAULT_GRID_HEIGHT = 600

# Nombres de los algoritmos de búsqueda
BFS = "Búsqueda por anchura"
DFS = "Búsqueda por profundidad"
UCS = "Búsqueda por costo uniforme"
ASTAR = "Búsqueda A*"

# Representación de los agentes en el mapa
GRASS = "C"
ROCK = "R"
METAL = "M"
BOMBERMAN = "S"
GOAL = "G"

# Colores para las celdas (usado en la representación visual)
COLOR_GRASS = "#00FF00"
COLOR_ROCK = "#808080"
COLOR_METAL = "#A9A9A9"

# Rutas de las imágenes de los agentes
IMG_BOMBERMAN = "project/assets/images/character/walk-right.png"
IMG_GRASS = "project/assets/images/terrain/grass.png"
IMG_ROCK = "project/assets/images/terrain/rock.png"
IMG_METAL = "project/assets/images/terrain/wall.png"
IMG_GROUND = "project/assets/images/terrain/ground.png"

# Rutas de los mapas
MAP_5X5 = "project/assets/maps/5x5.txt"
MAP_10X10 = "project/assets/maps/10x10.txt"
MAP_20X20 = "project/assets/maps/20x20.txt"

# Valores del selector de algoritmos
ALGORITHMS = [BFS, DFS, UCS, ASTAR]

# Títulos para los selectores
ALGORITHM_SELECTOR_TITLE = "Algoritmo de búsqueda"
MAP_SELECTOR_TITLE = "Mapa"
HEURISTIC_SELECTOR_TITLE = "Heurística"

# Valores del selector de heurísticas
HEURISTICS = ["Manhattan", "Euclidean"]

# Nombre del proyecto
PROJECT_NAME = "Bomberman v1.0"

# Puerto por defecto para el servidor
DEFAULT_PORT = 8521

# Descripción del proyecto
PROJECT_DESCRIPTION = """Proyecto de la asignatura de Sistemas Inteligentes 1. El proyecto trata de la simulación de un agente Bomberman 
                        que busca la salida en un laberinto, utilizando diferentes algoritmos de búsqueda.
                        
                        El agente Bomberman se mueve en un mapa de tamaño variable, en el que puede encontrar obstáculos como rocas y paredes de metal,
                        el objetivo del agente es encontrar la salida del laberinto, evitando los obstáculos y sin dejarse atrapar por los enemigos.

                        Las reglas del juego son las siguientes:
                        - El agente Bomberman se mueve en un mapa de tamaño variable.
                        - El agente Bomberman debe encontrar la salida del laberinto.
                        - El agente Bomberman no puede atravesar las rocas pero si las puede destruir para obtener mejoras en sus bombas.
                        - El agente Bomberman no puede atravesar las paredes de metal ni tampoco podrá destruirlas.
                        """

# Ruta por defecto donde se abrirá el explorador de archivos
DEFAULT_DIRECTORY_JHAIR = (
    "C:/Users/USUARIO/Documents/Universidad/2024-2/inteligentes1/project/assets/maps"
)
DEFAULT_DIRECTORY_JUAN = "/ruta/a/tu/carpeta/de/mapas"