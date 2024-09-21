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
    if agent.pos in agent.model.visited_cells:
        return {
            "Shape": get_image_path(IMG_GROUND),
            "Filled": "true",
            "Layer": 0,
            "w": 1,
            "h": 1,
        }
    else:
        return {
            "Shape": get_image_path(IMG_GRASS),
            "Filled": "true",
            "Layer": 0,
            "w": 1,
            "h": 1,
        }


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
