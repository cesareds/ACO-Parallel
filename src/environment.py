from src.ant import Ant
import json
import random
from colorama import init, Fore, Style

class Environment:
    def __init__(self, number_cols: int, number_rows: int, number_ants: int, number_process: int, number_obstacles: int, number_iterations: int, goalx: int, goaly: int, load_grid: bool = False) -> None:
        self.grid = []
        self.number_cols = number_cols
        self.number_rows = number_rows
        self.number_ants = number_ants
        self.number_process = number_process
        self.number_obstacles = number_obstacles
        self.number_iterations = number_iterations

        # Load grid from file or create a new one
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
            self.grid[goalx][goaly]["value"] = 1

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
        for it in range(self.number_iterations):
            print(f"Iteração {it}")
            for ant in self.ants:
                ant.reset()
                ant.run(self.grid)

            # Select the best ant that reached the goal
            best_ant = min((ant for ant in self.ants if ant.reached_goal), key=lambda a: a.cost, default=None)
            if best_ant:
                best_ant.update_pheromone(self.grid, Q=1.0)

            self.evaporate_pheromones(evaporation_rate)
        print("Cost final: ", best_ant.cost)
        print("\nFinal grid:")
        self.print_grid()
        self.save_grid_to_json(f"grid_{self.number_rows}x{self.number_cols}.json")

    def evaporate_pheromones(self, evaporation_rate: float = 0.5):
        for i in range(self.number_rows):
            for j in range(self.number_cols):
                for direction in self.grid[i][j]["pheromones"]:
                    self.grid[i][j]["pheromones"][direction] *= (1 - evaporation_rate)


    init()
    def print_grid(self):
        visited = set()
        for ant in self.ants:
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
        with open("grid_output.txt", "w") as f:
            for line in output_lines:
                f.write(line + "\n")
