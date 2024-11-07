from mesa.visualization.modules import CanvasGrid
from mesa.visualization.UserParam import Choice
from mesa.visualization.ModularVisualization import ModularServer
from services.map_service import load_map_from_file
from ui.map_selector import select_map
from agents.agent_portrayal import agent_portrayal
from models.bombermanModel import BombermanModel
from config.constants import *


def run_simulation():
    # Seleccionar el archivo de mapa
    map_file = select_map()
    if not map_file:
        print("No se seleccionó ningún archivo de mapa. Saliendo...")
        return

    # Cargar los datos del mapa
    map_data, pos_bomberman, pos_goal, width, height = load_map_from_file(map_file)

    # Crear el canvas
    grid = CanvasGrid(
        agent_portrayal, width, height, DEFAULT_GRID_WIDTH, DEFAULT_GRID_HEIGHT
    )

    # Parámetros del modelo
    model_params = {
        "width": width,
        "height": height,
        "map_data": map_data,
        "pos_goal": pos_goal,
        "pos_bomberman": pos_bomberman,
        "number_of_agents": 1,
        "search_algorithm": Choice(
            name=ALGORITHM_SELECTOR_TITLE,
            value=ALGORITHMS[0],
            choices=ALGORITHMS,
        ),
        "priority": Choice(
            name=PRIORITY_SELECTOR_TITLE,
            value=PRIORITIES[0],
            choices=PRIORITIES,
        ),
        "heuristic": Choice(
            name=HEURISTIC_SELECTOR_TITLE,
            value=HEURISTICS[0],
            choices=HEURISTICS,
        ),
        "balloons": Choice(
            name=BALLOONS_SELECTOR_TITLE,
            value=BALLOONS[0],
            choices=BALLOONS,
        ),
    }

    # Configurar el servidor para visualizar la simulación
    server = ModularServer(BombermanModel, [grid], PROJECT_NAME, model_params)

    server.description = PROJECT_DESCRIPTION

    server.port = DEFAULT_PORT
    server.launch()


if __name__ == "__main__":
    run_simulation()
