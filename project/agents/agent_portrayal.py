from agents import (
    BombermanAgent,
    GrassAgent,
    MetalAgent,
    RockAgent,
    BorderAgent,
    GoalAgent,
    BalloonAgent,
    BombAgent
)
from helpers.file_reader import get_image_path
from config.constants import (
    IMG_GRASS,
    IMG_GROUND,
    IMG_ROCK,
    IMG_METAL,
    IMG_BOMBERMAN,
    IMG_BORDER,
    IMG_GOAL,
    IMG_BALLOON,
    IMG_BOMB
)


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
    elif isinstance(agent, BorderAgent):
        return border_portrayal()
    elif isinstance(agent, GoalAgent):
        return goal_portrayal()
    elif isinstance(agent, BalloonAgent):
        portrayal["Shape"] = get_image_path(IMG_BALLOON)
        portrayal["Layer"] = 2
    elif isinstance(agent, BombermanAgent):
        portrayal["Shape"] = get_image_path(IMG_BOMBERMAN)
        portrayal["Layer"] = 2
    elif isinstance(agent, BombAgent):
        return bomb_portrayal()
    return portrayal

def bomb_portrayal():
    return {
        "Shape": get_image_path(IMG_BOMB),
        "Filled": "true",
        "Layer": 1,  # Layer superior para que sea visible sobre otros elementos
        "w": 1,
        "h": 1,
        "Color": "red"
    }

def grass_portrayal(agent):
    portrayal = {
        "Shape": "rect",
        "Filled": "true",
        "Layer": 0,
        "w": 1,
        "h": 1,
    }

    visit_info = next(
        (info for pos, info in agent.model.visited_cells if pos == agent.pos), None
    )

    if agent.pos in agent.model.visited_ground_cells:
        portrayal["Shape"] = get_image_path(IMG_GROUND)
        portrayal["text"] = str(visit_info) if visit_info else ""
        portrayal["text_color"] = "yellow"
    elif visit_info:
        portrayal["Shape"] = get_image_path(IMG_GRASS)
        portrayal["text"] = str(visit_info)
        portrayal["text_color"] = "white"
    else:
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


def border_portrayal():
    return {
        "Shape": get_image_path(IMG_BORDER),
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


def goal_portrayal():
    return {
        "Shape": get_image_path(IMG_GOAL),
        "Filled": "true",
        "Layer": 0,
        "w": 1,
        "h": 1,
    }
