from src.ant import Ant
import json
import random

class Environment:
    def __init__(self, number_cols: int, number_rows: int, number_ants: int, number_process: int, number_obstacles: int) -> None:
        self.grid = []
        self.number_cols = number_cols
        self.number_rows = number_rows
        self.number_ants = number_ants
        self.number_process = number_process
        self.number_obstacles = number_obstacles

        for _ in range(self.number_rows):
            row = []
            for _ in range(self.number_cols):
                row.append({
                    "value": random.choice([0, 0, 0, 0, 0, -1]),  # 1 cell is the goal
                    "pheromones": {
                        "up":   1e-6, 
                        "down": 1e-6, 
                        "left": 1e-6, 
                        "right": 1e-6
                    }
                })
            self.grid.append(row)

        # Agora fora do loop: define a célula final como objetivo
        self.grid[-1][-1]["value"] = 1


        # Initialize the ants' positions and goals
        self.ants = []
        for i in range(self.number_ants):
            self.ants.append(
                Ant(
                    start=(0, 0),  # Starting position can be set as needed
                    goal=(self.number_rows - 1, self.number_cols - 1),  # Goal can be set as needed
                    alpha=1.0, 
                    beta=2.0,
                    number_cols=self.number_cols,
                    number_rows=self.number_rows
                )
            ) 

    def save_grid_to_json(self, filename: str) -> None:
        with open(filename, 'w') as f:
            json.dump(self.grid, f, indent=4)

    def optimize(self, iterations=10_000, evaporation_rate=0.1):
        for it in range(iterations):
            costs = []
            for ant in self.ants:
                # print("----------------------- new ant -----------------------")
                ant.reset()
                cost = ant.run(self.grid)
                
            best_ant = min((ant for ant in self.ants if ant.reached_goal), key=lambda a: a.cost, default=None)
            if best_ant:
                best_ant.update_pheromone(self.grid, Q=1.0)


            self.evaporate_pheromones(evaporation_rate)

        print("\nGrid final:")
        self.print_grid()


    def evaporate_pheromones(self, evaporation_rate: float = 0.5):
        for i in range(self.number_rows):
            for j in range(self.number_cols):
                for direction in self.grid[i][j]["pheromones"]:
                    self.grid[i][j]["pheromones"][direction] *= (1 - evaporation_rate)


    def print_grid(self):
        visited = set()
        for ant in self.ants:
            visited.update(ant.visited_nodes)

        for i in range(self.number_rows):
            row_str = ""
            for j in range(self.number_cols):
                if (i, j) == self.ants[0].start:
                    row_str += "S "
                elif self.grid[i][j]["value"] == 1:
                    row_str += "G "
                elif self.grid[i][j]["value"] == -1:
                    row_str += "M "
                elif (i, j) in visited:
                    row_str += "* "
                else:
                    row_str += ". "
            print(row_str)
