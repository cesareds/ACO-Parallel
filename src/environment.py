from src.ant import Ant
import json
import random
from colorama import init, Fore, Style
import multiprocessing as mp

class Environment:
    def __init__(self, number_cols: int, number_rows: int, number_ants: int, number_process: int, number_obstacles: int, number_iterations: int, goalx: int, goaly: int, load_grid: bool) -> None:
        self.grid = []
        self.number_cols = number_cols
        self.number_rows = number_rows
        self.number_ants = number_ants
        self.number_process = number_process
        self.number_obstacles = number_obstacles
        self.number_iterations = number_iterations

        """
        Lista com conexoes para os processos que estao rodando em paralelo

        É por aqui que o Mestre vai se comunicar com os Workers
        Cada Worker vai possuir um "TCP" com o Mestre 
        """ 
        self.connections = [] 
        self.running_processes = []


        if load_grid:
            self.load_grid_from_json(f"grid_{self.number_rows}x{self.number_cols}.json")
        else:
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

            # Set the goal cell at the bottom-right corner
            self.grid[goaly][goalx]["value"] = 1

        # Initialize ants with start and goal positions
        self.ants = []
        for i in range(self.number_ants):
            self.ants.append(
                Ant(
                    start=(0, 0),
                    goal=(self.number_rows - 1, self.number_cols - 1),
                    alpha=1.0,
                    beta=5.0,
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

    def optimize(self, evaporation_rate=0.1):
        best_ant_ever = None
        for it in range(self.number_iterations):
            print(f"Iteração {it}")
            for ant in self.ants:
                ant.reset()
                ant.run(self.grid)

            # Select the best ant that reached the goal
            best_ant = min((ant for ant in self.ants if ant.reached_goal), key=lambda a: a.cost, default=None)
            if best_ant:
                best_ant_ever = best_ant
                best_ant.update_pheromone(self.grid, Q=1.0)

            self.evaporate_pheromones(evaporation_rate)
        if best_ant:
            print("Cost final: ", best_ant.cost)
        print("\nFinal grid:")
        self.print_grid(best_ant_ever)
        # self.save_grid_to_json(f"grid_{self.number_rows}x{self.number_cols}.json")

    def evaporate_pheromones(self, evaporation_rate: float = 0.5):
        for i in range(self.number_rows):
            for j in range(self.number_cols):
                for direction in self.grid[i][j]["pheromones"]:
                    self.grid[i][j]["pheromones"][direction] *= (1 - evaporation_rate)

    def print_grid(self, ant):
        init()
        visited = set()
        visited.update(ant.visited_nodes)

        output_lines = []  # Armazena as linhas para salvar no .txt

        for i in range(self.number_rows):
            row_str = ""
            row_plain = ""  # Versão sem as cores ANSI
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

        # Escreve a saída "limpa" em um arquivo .txt
        with open("grids/grid_output.txt", "w") as f:
            for line in output_lines:
                f.write(line + "\n")

    def optimize_mp(self):
        ants_per_process = int(self.number_ants / self.number_process)

        for j in range(self.number_iterations):
            print(j)
            # Divide as formigas entre os processos
            argumentos = [
                (self.ants[i * ants_per_process: (i + 1) * ants_per_process], self.grid, i)
                for i in range(self.number_process)
            ]

            best_ants = []
            best_ant = None
            with mp.Pool(self.number_process) as pool:
                # Isso já faz join automaticamente no final
                best_ant = pool.map(worker, argumentos)
                # print("retorno", best_ant)
                best_ants.extend(best_ant)

            best_ant = min((ant for ant in best_ants if ant.reached_goal), key=lambda a: a.cost, default=None)

            if best_ant:
                # print("Melhor custo", best_ant.cost)
                best_ant.update_pheromone(self.grid, Q=1.0)

        self.print_grid(best_ant)
        # self.save_grid_to_json(f"grid_{self.number_rows}x{self.number_cols}.json")

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


        for j in range(self.number_iterations-1):
            print(j)

            best_ant = self.get_best_ant()

            if best_ant:
                best_ant.update_pheromone(self.grid, Q=1.0)
            
            self.send_broadcast_msg(self.grid)


        self.send_broadcast_msg(None)

        self.print_grid(best_ant)
        # self.save_grid_to_json(f"grid_{self.number_rows}x{self.number_cols}.json")

def worker_pipie(ants, grid, id, connection_to_main):

    while True:
        for ant in ants:
            ant.reset()
            ant.run(grid)

        # Select the best ant that reached the goal
        best_ant = min((ant for ant in ants if ant.reached_goal), key=lambda a: a.cost, default=None)

        connection_to_main.send(best_ant if best_ant else ants[-1])

        grid = connection_to_main.recv()

        if grid == None:
            # Se grid for None, significa que acabou as iterações e o processo pode morrer
            return

def worker(args):
    ants, grid, id = args
    for ant in ants:
        ant.reset()
        ant.run(grid)

    # Select the best ant that reached the goal
    best_ant = min((ant for ant in ants if ant.reached_goal), key=lambda a: a.cost, default=None)
    # print(f"Melhor formuga {best_ant} - id {id}")
    # print(id)
    return best_ant if best_ant else ants[-1]