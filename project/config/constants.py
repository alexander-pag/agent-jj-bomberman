# Nombres de los agentes
BOMBERMAN_AGENT = "Bomberman"
GRASS_AGENT = "Grass"
ROCK_AGENT = "Rock"
METAL_AGENT = "Metal"
POWER_AGENT = "Power"

# Dimensiones por defecto del grid
DEFAULT_GRID_WIDTH = 600
DEFAULT_GRID_HEIGHT = 600

# Nombres de los algoritmos de búsqueda
BFS = "Búsqueda por anchura"
DFS = "Búsqueda por profundidad"
UCS = "Búsqueda por costo uniforme"
ASTAR = "Búsqueda A*"
BEAM = "Búsqueda Beam Search"
HILL = "Búsqueda Hill Climbing"
ALPHA_BETA = "Poda Alfa Beta"

# Representación de los agentes en el mapa
GRASS = "C"
ROCK = "R"
METAL = "M"
BOMBERMAN = "S"
GOAL = "G"
BORDER = "X"
BALLOON = "B"

# Colores para las celdas (usado en la representación visual)
COLOR_GRASS = "#00FF00"
COLOR_ROCK = "#808080"
COLOR_METAL = "#A9A9A9"

# Rutas de las imágenes de los agentes
IMG_BOMBERMAN = "project/assets/images/character/bomberman.png"
IMG_GRASS = "project/assets/images/terrain/grass.png"
IMG_ROCK = "project/assets/images/terrain/wall1.png"
IMG_BORDER = "project/assets/images/terrain/border.png"
IMG_METAL = "project/assets/images/terrain/metal.png"
IMG_GOAL = "project/assets/images/terrain/goal.png"
IMG_GROUND = "project/assets/images/terrain/ground1.png"
IMG_BALLOON = "project/assets/images/enemies/balloon/balloon2.png"
IMG_BOMB = "project/assets/images/items/bomb.png"
IMG_EXPLOSION = "project/assets/images/items/explosion.png"
IMG_POWER = "project/assets/images/items/power.png"

# Rutas de los mapas
MAP_5X5 = "project/assets/maps/5x5.txt"
MAP_10X10 = "project/assets/maps/10x10.txt"
MAP_20X20 = "project/assets/maps/20x20.txt"
MAP_20X20_1 = "project/assets/maps/20x20_1.txt"
MAP_20X20_2 = "project/assets/maps/20x20_2.txt"
MAP_20X20_3 = "project/assets/maps/20x20_3.txt"

# Valores del selector de algoritmos
ALGORITHMS = [BFS, DFS, UCS, ASTAR, BEAM, HILL, ALPHA_BETA]

ACTOR_SYMBOLS = {
    "Bomberman": "S",
    "Enemy": "B",
    "Goal": "G",
    "S":"S",
    "B":"B",
    "G":"G",
}


# Títulos para los selectores
ALGORITHM_SELECTOR_TITLE = "Algoritmo de búsqueda"
MAP_SELECTOR_TITLE = "Mapa"
HEURISTIC_SELECTOR_TITLE = "Heurística"
PRIORITY_SELECTOR_TITLE = "Prioridad"
BALLOONS_SELECTOR_TITLE = "Número de enemigos"
DIFICULTY_SELECTOR_TITLE = "Dificultad"
NUMBER_POWERS_SELECTOR_TITLE = "Número de poderes"

# Valores del selector de heurísticas
HEURISTICS = ["Manhattan", "Euclidean"]

# Valores del selector de enemigos
BALLOONS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# Valores del selector de prioridades
PRIORITIES = [
    "Izquierda, Arriba, Derecha, Abajo",
    "Arriba, Abajo, Derecha, Izquierda",
    "Arriba, Derecha, Abajo, Izquierda",
    "Arriba, Izquierda, Abajo, Derecha",
    "Derecha, Izquierda, Abajo, Arriba",
]

TURN = "Bomberman"

# Valores del selector de dificultades
DIFFICULTIES = [1, 2, 3]

# Valores del selector de número de poderes
NUMBER_POWERS = [1, 2, 3, 4, 5]

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
