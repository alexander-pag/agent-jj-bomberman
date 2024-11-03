from mesa import Agent
from algorithms import astar_search, bfs, ucs, dfs, beam_search, hill_climbing
from config.constants import *
import logging
from agents.rockAgent import RockAgent
from agents.bombAgent import BombAgent
from agents.explosionAgent import ExplosionAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BombermanAgent(Agent):
    def __init__(self, unique_id, model, start_pos):
        super().__init__(unique_id, model)
        self.pos = start_pos
        self.path = None
        self.goal = model.pos_goal
        self.history = []
        self.rocks = []
        self.retreat_steps = []
        self.waiting_for_explosion = False
        self.algorithms = {
            DFS: dfs,
            UCS: ucs,
            BFS: bfs,
            ASTAR: astar_search,
            BEAM: beam_search,
            HILL: hill_climbing,
        }

    def step(self) -> None:
        """Método que se ejecuta en cada paso del modelo."""
        if self.verify_exit():
            self.model.running = False
            return

        self.move()

    def verify_exit(self) -> bool:
        """Verifica si Bomberman ha alcanzado la salida."""
        return self.pos == self.goal

    def move(self) -> None:
        """Gestiona el movimiento del agente Bomberman."""
        if self.path is None or not self.path:
            self.calculate_path()

        if self.path:
            self.follow_path()

    def calculate_path(self) -> None:
        """Calcula el camino hacia la meta utilizando el algoritmo seleccionado."""
        algorithm = self.algorithms.get(self.model.search_algorithm)

        logger.info(
            f"Ejecutando juego con: {self.model.search_algorithm} y prioridad: {self.model.priority}. {self.model.heuristic}"
        )

        if algorithm:
            if (
                self.model.search_algorithm == ASTAR
                or self.model.search_algorithm == BEAM
                or self.model.search_algorithm == HILL
            ):
                self.path, visited_order = algorithm(
                    self.pos,
                    self.goal,
                    self.model,
                    self.model.heuristic,
                )
            else:
                self.path, visited_order, self.rocks = algorithm(
                    self.pos, self.goal, self.model
                )

            print("las rocas son: ", self.rocks)

            if self.path is None:
                logger.warning(
                    f"No se encontró un camino desde {self.pos} hasta {self.goal}"
                )
            else:
                # Guardar el orden en que se visitaron los nodos
                self.model.visited_cells = [
                    (pos, idx + 1) for idx, pos in enumerate(visited_order)
                ]

                # Guardar las celdas que son parte del camino final
                self.model.final_path_cells = set(self.path)
        else:
            logger.error(
                f"Algoritmo de búsqueda desconocido: {self.model.search_algorithm}"
            )

    def follow_path(self) -> None:
        """Sigue el camino calculado, moviéndose a la siguiente posición."""
        if self.path:
            next_step = self.path.pop(0)
            previus_pos = self.pos

            # si la siguiente posición es una roca plantar bomba
            if self.is_rock(next_step):
                bomb_agent = BombAgent(self.model.next_id(), self.model, 1, previus_pos)
                self.model.grid.place_agent(bomb_agent, previus_pos)
                self.model.schedule.step()

            self.model.grid.move_agent(self, next_step)
            self.pos = next_step

            if self.pos not in [pos for pos, _ in self.model.visited_cells]:
                visit_number = len(self.model.visited_cells) + 1
                self.model.visited_cells.append((self.pos, visit_number))

            if self.pos not in self.model.visited_ground_cells:
                self.model.visited_ground_cells.add(self.pos)

        if self.verify_exit():
            self.model.running = False

    def is_rock(self, pos):
        """
        Verifica si en la posición pos hay una roca.
        """
        agents = self.model.grid.get_cell_list_contents([pos])
        return any(isinstance(agent, RockAgent) for agent in agents)

    def place_bomb(self, next_position):
        self.rocks.remove(next_position)
        bomb_agent = BombAgent(
            self.model.schedule.get_agent_count(), self.model, 1, self.pos
        )
        self.model.schedule.add(bomb_agent)
        self.model.grid.place_agent(bomb_agent, self.pos)
        self.waiting_for_explosion = True

        # Genera los pasos de retroceso en función del cooldown de la bomba usando el historial.
        cooldown_steps = bomb_agent.cooldown
        if len(self.history) >= cooldown_steps:
            # Toma las últimas posiciones recorridas para retroceder.
            self.retreat_steps = self.history[-cooldown_steps:]
            self.retreat_steps.reverse()  # Asegura que retroceda en el orden correcto.
            # Limpia el historial para evitar un retroceso innecesario en futuros pasos.
            self.history = self.history[:-cooldown_steps]
        else:
            self.retreat_steps = self.history[
                ::-1
            ]  # Retrocede todas las posiciones si no hay suficientes.
            self.history = []

    def check_explosion_status(self):
        bombs = [
            agent
            for agent in self.model.schedule.agents
            if isinstance(agent, BombAgent)
        ]
        explosions = [
            agent
            for agent in self.model.schedule.agents
            if isinstance(agent, ExplosionAgent)
        ]
        if not bombs and not explosions and self.waiting_for_explosion:
            print("Bomba explotó, comenzando regreso al punto de la bomba.")
            self.waiting_for_explosion = False
