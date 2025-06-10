from src.ant import Ant
import json
import random
from colorama import init, Fore, Style
import multiprocessing as mp

class Environment:
    def __init__(self, number_cols: int, number_rows: int, number_ants: int, number_process: int, number_iterations: int, goalx: int, goaly: int, alpha: float, beta: float, evaporation_rate: float) -> None:
        self.grid = []
        self.number_cols = number_cols
        self.number_rows = number_rows
        self.number_ants = number_ants
        self.number_process = number_process
        self.number_iterations = number_iterations
        self.evaporation_rate = evaporation_rate

        """
        Lista com conexoes para os processos que estao rodando em paralelo

        É por aqui que o Mestre vai se comunicar com os Workers
        Cada Worker vai possuir um "TCP" com o Mestre 
        """ 
        self.connections = [] 
        self.running_processes = []


        try:
            self.load_grid_from_json(f"grid_{self.number_rows}x{self.number_cols}.json")
        except FileNotFoundError:
            for _ in range(self.number_rows):
                row = []
                for _ in range(self.number_cols):
                    row.append({
                        "value": random.choice([0, 0, 0, 0, 0, 0, 0, 0, -1]),  # obstacle = -1
                        "pheromones": {
                            "up":   1e-6,
                            "down": 1e-6,
                            "left": 1e-6,
                            "right": 1e-6
                        }
                    })
                self.grid.append(row)

            self.grid[goaly][goalx]["value"] = 1

            self.save_grid_to_json(f"grids/grid_{self.number_rows}x{self.number_cols}.json")

        self.ants = []
        for i in range(self.number_ants):
            self.ants.append(
                Ant(
                    start=(0, 0),
                    goal=(self.number_rows - 1, self.number_cols - 1),
                    alpha=alpha,
                    beta=beta,
                    number_cols=self.number_cols,
                    number_rows=self.number_rows
                )
            )

    def save_grid_to_json(self, filename: str) -> None:
        with open(filename, 'w') as f:
            json.dump(self.grid, f, indent=4)

    def load_grid_from_json(self, filename: str) -> None:
        with open(filename, 'r') as f:
            self.grid = json.load(f)

        self.number_rows = len(self.grid)
        self.number_cols = len(self.grid[0]) if self.grid else 0

    def optimize(self):
        best_ant_ever = None
        for it in range(self.number_iterations):
            print(f"Iteração {it}")
            for ant in self.ants:
                ant.reset()
                ant.run(self.grid)

            best_ant = min((ant for ant in self.ants if ant.reached_goal), key=lambda a: a.cost, default=None)
            if best_ant:
                best_ant_ever = best_ant
                best_ant.update_pheromone(self.grid, Q=1.0)

            self.evaporate_pheromones()
        if best_ant_ever:
            print("Cost final: ", best_ant_ever.cost)
        self.print_grid(best_ant_ever)

    def evaporate_pheromones(self):
        for i in range(self.number_rows):
            for j in range(self.number_cols):
                for direction in self.grid[i][j]["pheromones"]:
                    self.grid[i][j]["pheromones"][direction] *= (1 - self.evaporation_rate)

    def print_grid(self, ant):
        init()
        visited = set()
        if ant is not None:
            visited.update(ant.visited_nodes)

        output_lines = [] 

        for i in range(self.number_rows):
            row_str = ""
            row_plain = ""  
            for j in range(self.number_cols):
                if (i, j) == self.ants[0].start:
                    row_str += Fore.BLUE + "S " + Style.RESET_ALL
                    row_plain += "S "
                elif self.grid[i][j]["value"] == 1:
                    row_str += Fore.BLUE + "G " + Style.RESET_ALL
                    row_plain += "G "
                elif self.grid[i][j]["value"] == -1:
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
            
        self.save_grid_to_json(f"grids/grid_{self.number_rows}x{self.number_cols}_solved.json")


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
                    target=worker_pipie, args=(self.ants[i * ants_per_process: (i + 1) * ants_per_process], self.grid, i, connection_to_main)
                )
            )

        for process in self.running_processes:
            process.start()


        best_ant_ever = None
        for j in range(self.number_iterations-1):
            # print(j)

            best_ant = self.get_best_ant()

            if best_ant:
                best_ant.update_pheromone(self.grid, Q=1.0)
                best_ant_ever = best_ant
            

            self.evaporate_pheromones()
            self.send_broadcast_msg(self.grid)

        print(best_ant_ever.cost if best_ant_ever else "Nenhum ant alcançou o objetivo")
        self.send_broadcast_msg(None)
        # self.print_grid(best_ant)

def worker_pipie(ants, grid, id, connection_to_main):
    try:
        while True:
            for ant in ants:
                ant.reset()
                ant.run(grid)

            best_ant = min((ant for ant in ants if ant.reached_goal), key=lambda a: a.cost, default=None)

            try:
                connection_to_main.send(best_ant if best_ant else ants[-1])
            except (BrokenPipeError, EOFError):
                return

            grid = connection_to_main.recv()
            if grid is None:
                return
    except (BrokenPipeError, EOFError):
        return
