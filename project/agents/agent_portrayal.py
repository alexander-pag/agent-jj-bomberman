from agents import BombermanAgent, GrassAgent, MetalAgent, RockAgent
from helpers.file_reader import get_image_path
from config.constants import IMG_GRASS, IMG_GROUND, IMG_ROCK, IMG_METAL, IMG_BOMBERMAN


def agent_portrayal(agent) -> dict:
    """
    Define cómo se visualizarán los agentes en la simulación.

    Args:
        agent: Agente a visualizar.

    Returns:
        Diccionario con la configuración de visualización del agente.
    """
    portrayal = {"Shape": "circle", "Filled": "true", "r": 0.5}

    if isinstance(agent, GrassAgent):
        return grass_portrayal(agent)
    elif isinstance(agent, RockAgent):
        return rock_portrayal()
    elif isinstance(agent, MetalAgent):
        return metal_portrayal()
    elif isinstance(agent, BombermanAgent):
        portrayal["Shape"] = get_image_path(IMG_BOMBERMAN)
        portrayal["Layer"] = 1
    return portrayal


def grass_portrayal(agent):
    portrayal = {
        "Shape": "rect",
        "Filled": "true",
        "Layer": 0,
        "w": 1,
        "h": 1,
    }

    # Buscar si la celda ha sido visitada
    visit_info = next(
        (info for pos, info in agent.model.visited_cells if pos == agent.pos), None
    )

    if visit_info:
        # Si ha sido visitada, mostrar el número de visita
        portrayal["Shape"] = get_image_path(IMG_GROUND)
        portrayal["text"] = str(visit_info)
        portrayal["text_color"] = "white"
    else:
        # Si no ha sido visitada, mostrar césped
        portrayal["Shape"] = get_image_path(IMG_GRASS)

    return portrayal


def rock_portrayal():
    return {
        "Shape": get_image_path(IMG_ROCK),
        "Filled": "true",
        "Layer": 0,
        "w": 1,
        "h": 1,
    }


def metal_portrayal():
    return {
        "Shape": get_image_path(IMG_METAL),
        "Filled": "true",
        "Layer": 0,
        "w": 1,
        "h": 1,
    }
