from mesa import Agent
from algorithms import *
from config.constants import *
from agents.rockAgent import RockAgent
from agents.bombAgent import BombAgent
from agents.metalAgent import MetalAgent
from agents.explosionAgent import ExplosionAgent
import random


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
            ALPHA_BETA: minimax,
        }
        self.time_steps = 0

    def step(self) -> None:
        """Realiza un paso en la simulación."""
        self.time_steps += 1

        if self.waiting_for_explosion:
            # Verificar si hay que retroceder
            if self.retreat_steps:
                next_retreat = self.retreat_steps.pop(0)
                self.model.grid.move_agent(self, next_retreat)
                self.pos = next_retreat
            # Si ya terminamos de retroceder y la explosión terminó
            elif self.check_explosion_status():
                self.waiting_for_explosion = False
                # Recalcular el camino desde la posición actual
                self.calculate_path()  # Usamos el método existente
                print(f"Camino recalculado desde posición {self.pos}")
        else:
            self.move_to(self.pos)

    def verify_exit(self) -> bool:
        """Verifica si Bomberman ha alcanzado la salida."""
        return self.pos == self.goal

    def move(self) -> None:
        if self.path is None or not self.path:
            self.calculate_path()

        if self.path:
            self.follow_path()

    def calculate_path(self) -> None:
        """Calcula el camino hacia la meta utilizando el algoritmo seleccionado."""
        algorithm = self.algorithms.get(self.model.search_algorithm)

        if algorithm and self.model.search_algorithm != ALPHA_BETA:
            result = (
                algorithm(self.pos, self.goal, self.model, self.model.heuristic)
                if self.model.search_algorithm in (ASTAR, BEAM, HILL)
                else algorithm(self.pos, self.goal, self.model)
            )

            # Verifica el número de valores retornados
            if len(result) == 3:
                self.path, visited_order, self.rocks = result
            elif len(result) == 2:
                self.path, visited_order = result
                self.rocks = []  # Inicializa rocks si no se devolvió

            # Guardar el orden en que se visitaron los nodos
            self.model.visited_cells = [
                (pos, idx + 1) for idx, pos in enumerate(visited_order)
            ]

            # Guardar las celdas que son parte del camino final
            self.model.final_path_cells = set(self.path)

    def follow_path(self) -> None:
        """Sigue el camino calculado, moviéndose a la siguiente posición."""
        if not self.path:
            return

        next_step = self.path[0]

        # Verificar si hay una roca en la siguiente posición
        if self.is_rock(next_step):
            # Colocar bomba solo si no estamos ya esperando una explosión
            if not self.waiting_for_explosion:
                bomb_agent = BombAgent(self.model.next_id(), self.model, self.pos)
                self.model.grid.place_agent(bomb_agent, self.pos)
                self.model.schedule.add(bomb_agent)
                self.waiting_for_explosion = True

                # Calcula pasos de retroceso
                cooldown_steps = bomb_agent.cooldown
                if len(self.history) >= cooldown_steps:
                    self.retreat_steps = self.history[-cooldown_steps:]
                    self.retreat_steps.reverse()
                    self.history = self.history[:-cooldown_steps]
                else:
                    self.retreat_steps = self.history[::-1]
                    self.history = []
            return

        # Si no hay roca o la explosión ya ocurrió, podemos movernos
        if not self.waiting_for_explosion:
            next_step = self.path.pop(0)
            previus_pos = self.pos

            self.model.grid.move_agent(self, next_step)
            self.pos = next_step

            self.history.append(previus_pos)

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

    def check_explosion_status(self):
        """
        Verifica el estado de la explosión y si el muro fue destruido.
        Retorna True si podemos continuar moviéndonos.
        """
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

        # Solo continuamos si no hay bombas ni explosiones activas y hemos terminado de retroceder
        if (
            not bombs
            and not explosions
            and self.waiting_for_explosion
            and not self.retreat_steps
        ):
            print("Explosión completada y retroceso terminado, recalculando ruta")
            return True
        return False

    def move_to(self, new_pos):
        """
        Mueve a Bomberman a la nueva posición new_pos.
        """
        if self.path is None or not self.path:
            self.calculate_path()

        if self.path:
            self.follow_path()

        if self.model.search_algorithm == ALPHA_BETA:
            if not self.is_obstacle(new_pos):
                self.model.grid.move_agent(self, new_pos)
                self.pos = new_pos
                return True
            return False

    def is_obstacle(self, pos):
        """
        Verifica si hay un obstáculo en la posición pos.
        """
        cellmates = self.model.grid.get_cell_list_contents([pos])
        for agent in cellmates:
            if isinstance(agent, RockAgent) or isinstance(agent, MetalAgent):
                return True
        return False
