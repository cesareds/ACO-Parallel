import json
import cupy as cp
from src.ant import Ant
from colorama import init, Fore, Style
import multiprocessing as mp


def worker_pipie(ants, grid_values, pheromones, id, connection_to_main):
    try:
        while True:
            for ant in ants:
                ant.reset()
                ant.run(grid_values, pheromones)

            best_ant = min((ant for ant in ants if ant.reached_goal), key=lambda a: a.cost, default=None)

            try:
                connection_to_main.send(best_ant if best_ant else ants[-1])
            except (BrokenPipeError, EOFError):
                return

            msg = connection_to_main.recv()
            if msg is None:
                return
            grid_values, pheromones = msg
    except (BrokenPipeError, EOFError):
        return


class Environment:
    def __init__(self, number_cols, number_rows, number_ants, number_process,
                 number_iterations, goalx, goaly, alpha, beta, evaporation_rate, file) -> None:
        self.number_cols = number_cols
        self.number_rows = number_rows
        self.number_ants = number_ants
        self.number_process = number_process
        self.number_iterations = number_iterations
        self.alpha = alpha
        self.beta = beta
        self.evaporation_rate = evaporation_rate
        self.file = file

        self.connections = []
        self.running_processes = []

        try:
            self.load_grid_from_json(f"grids/grid_{number_rows}x{number_cols}.json")
        except FileNotFoundError:
            values = cp.random.choice(cp.array([0]*8 + [-1]), size=(number_rows, number_cols))
            values[goaly, goalx] = 1  # define o objetivo

            self.grid_values = values
            self.pheromones = cp.full((number_rows, number_cols, 4), 1e-6, dtype=cp.float32)

            self.save_grid_to_json(f"grids/grid_{number_rows}x{number_cols}.json")

        self.ants = [
            Ant(start=(0, 0), goal=(number_rows - 1, number_cols - 1),
                alpha=alpha, beta=beta, number_cols=number_cols, number_rows=number_rows)
            for _ in range(number_ants)
        ]

    def save_grid_to_json(self, filename):
        data = []
        for i in range(self.number_rows):
            row = []
            for j in range(self.number_cols):
                cell = {
                    "value": int(cp.asnumpy(self.grid_values[i, j])),
                    "pheromones": {
                        "up":   float(cp.asnumpy(self.pheromones[i, j, 0])),
                        "down": float(cp.asnumpy(self.pheromones[i, j, 1])),
                        "left": float(cp.asnumpy(self.pheromones[i, j, 2])),
                        "right":float(cp.asnumpy(self.pheromones[i, j, 3]))
                    }
                }
                row.append(cell)
            data.append(row)
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)

    def load_grid_from_json(self, filename):
        with open(filename, 'r') as f:
            raw_grid = json.load(f)

        self.grid_values = cp.zeros((len(raw_grid), len(raw_grid[0])), dtype=cp.int32)
        self.pheromones = cp.zeros((len(raw_grid), len(raw_grid[0]), 4), dtype=cp.float32)

        direction_map = {"up": 0, "down": 1, "left": 2, "right": 3}
        for i, row in enumerate(raw_grid):
            for j, cell in enumerate(row):
                self.grid_values[i, j] = cell["value"]
                for d, val in cell["pheromones"].items():
                    self.pheromones[i, j, direction_map[d]] = val

    def evaporate_pheromones(self):
        self.pheromones *= (1.0 - self.evaporation_rate)

    def optimize(self):
        best_ant_ever = None
        for it in range(self.number_iterations):
            for ant in self.ants:
                ant.reset()
                ant.run(self.grid_values, self.pheromones)

            best_ant = min((a for a in self.ants if a.reached_goal), key=lambda a: a.cost, default=None)
            if best_ant:
                best_ant_ever = best_ant
                best_ant.update_pheromone(self.pheromones, Q=1.0)

            self.evaporate_pheromones()

        print("Cost final:", best_ant_ever.cost if best_ant_ever else "Nenhum ant alcançou o objetivo")
        self.print_grid(best_ant_ever)

    def print_grid(self, ant):
        init()
        visited = set()
        if ant:
            visited.update(ant.visited_nodes)

        output_lines = []
        for i in range(self.number_rows):
            row_str = ""
            row_plain = ""
            for j in range(self.number_cols):
                val = int(cp.asnumpy(self.grid_values[i, j]))
                if (i, j) == self.ants[0].start:
                    row_str += Fore.BLUE + "S " + Style.RESET_ALL
                    row_plain += "S "
                elif val == 1:
                    row_str += Fore.BLUE + "G " + Style.RESET_ALL
                    row_plain += "G "
                elif val == -1:
                    row_str += Fore.RED + "M " + Style.RESET_ALL
                    row_plain += "M "
                elif (i, j) in visited:
                    row_str += Fore.GREEN + "* " + Style.RESET_ALL
                    row_plain += "* "
                else:
                    row_str += Fore.LIGHTWHITE_EX + ". " + Style.RESET_ALL
                    row_plain += ". "
            print(row_str)
            output_lines.append(row_plain)

        with open("grids/grid_output_solved.txt", "w") as f:
            for line in output_lines:
                f.write(line + "\n")

        self.save_grid_to_json(f"grids/grid_{self.number_rows}x{self.number_cols}_{self.alpha}_{self.beta}_{self.evaporation_rate}_{self.file}_solved.json")

    def send_broadcast_msg(self, msg):
        for connection in self.connections:
            connection.send(msg)

    def get_best_ant(self):
        ants = []
        for connection in self.connections:
            ants.append(connection.recv())

        return min((ant for ant in ants if ant.reached_goal), key=lambda a: a.cost, default=None)

    def optimize_mp_pipes_n_queues(self):
        ants_per_process = int(self.number_ants / self.number_process)

        for i in range(self.number_process):
            connection_to_main, connection_to_worker = mp.Pipe(duplex=True)

            self.connections.append(connection_to_worker)

            self.running_processes.append(
                mp.Process(
                    target=worker_pipie,
                    args=(self.ants[i * ants_per_process: (i + 1) * ants_per_process],
                          self.grid_values, self.pheromones, i, connection_to_main)
                )
            )

        for process in self.running_processes:
            process.start()

        best_ant_ever = None
        for j in range(self.number_iterations - 1):
            print(j)

            best_ant = self.get_best_ant()

            if best_ant:
                best_ant.update_pheromone(self.pheromones, Q=1.0)
                best_ant_ever = best_ant

            self.evaporate_pheromones()
            self.send_broadcast_msg((self.grid_values, self.pheromones))

        print("Cost final: ", best_ant_ever.cost if best_ant_ever else "Nenhum ant alcançou o objetivo")
        self.send_broadcast_msg(None)
        self.print_grid(best_ant_ever)