import math
import random

class Ant:
    """
    The drones from the original problem are represented as ants.
    Each ant has a current position, a list of visited nodes, and a tabu list.
    """
    def __init__(self, start: tuple, goal: tuple, alpha: float, beta: float) -> None:
        self.goal           = goal
        self.start          = start
        self.cur_position   = (self.start[0], self.start[1])
        self.visited_nodes  = [self.cur_position]
        self.alpha          = alpha
        self.beta           = beta
        self.reached_goal   = False

    @property
    def cost(self) -> int:
        return len(self.visited_nodes)
    

    def manhattan_distance(self, a: tuple, b: tuple) -> float:
        return abs(a[0] - b[0]) + abs(a[1] - b[1])


    def reset(self) -> None:
        self.cur_position   = (self.start[0], self.start[1])
        self.visited_nodes  = [self.cur_position]
        self.reached_goal   = False 

    def get_pheromone(self, from_pos: tuple, to_pos: tuple, grid: list[list[dict]]) -> float:
        x1, y1 = from_pos
        x2, y2 = to_pos
        dx, dy = x2 - x1, y2 - y1

        direction = None
        if dx == -1:
            direction = "up"
        elif dx == 1:
            direction = "down"
        elif dy == -1:
            direction = "left"
        elif dy == 1:
            direction = "right"

        if direction:
            return grid[x1][y1]["pheromones"].get(direction, 1e-6)
        return 1e-6  # movimento inválido

    def neighbors_probabilities(self, allowed_nodes: list[tuple], grid: list[list[dict]]) -> list[float]:
        probabilities = []
        denominator = 0.0

        for node in allowed_nodes:
            tau = self.get_pheromone(self.cur_position, node, grid)
            eta = 1 / (self.manhattan_distance(self.cur_position, node))   # Evita divisão por zero
            # print(f"ETA {eta} - {self.cur_position}")
            prob = (tau ** self.alpha) * (eta ** self.beta)

            probabilities.append(prob)
            denominator += prob

        if denominator == 0:
            return [1 / len(allowed_nodes)] * len(allowed_nodes)

        return [p / denominator for p in probabilities]

    def move(self, next_position: tuple, grid: list[list[dict]]) -> None:
        self.cur_position = next_position
        self.visited_nodes.append(next_position)

        x, y = next_position
        if grid[x][y]["value"] == 1:
            self.reached_goal = True
            # Atualiza feromônios ao alcançar o objetivo

    def get_neighbors(self, grid: list[list[dict]]) -> list[tuple]:
        x, y = self.cur_position
        neighbors = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for dx, dy in directions:
            new_x, new_y = x + dx, y + dy

            if new_x < 0:
                new_x = len(grid) - 1
            elif new_x >= len(grid):
                new_x = 0
            if new_y < 0:
                new_y = len(grid[0]) - 1
            elif new_y >= len(grid[0]):
                new_y = 0

            # print(f"New position: ({new_x}, {new_y}) from current position: ({x}, {y})")
            # print(f"Valor da posicao {grid[new_x][new_y]['value']}")
            if grid[new_x][new_y]["value"] >= 0 and (new_x, new_y) not in self.visited_nodes:
                neighbors.append((new_x, new_y))

        return neighbors

    def update_pheromone(self, grid: list[list[dict]], Q: float) -> None:
        """
        Atualiza os feromônios nas arestas percorridas pela formiga.
        grid: matriz com valores e feromônios
        Q: constante para atualização
        """
        for i in range(len(self.visited_nodes) - 1):
            from_node = self.visited_nodes[i]
            to_node = self.visited_nodes[i + 1]

            x1, y1 = from_node
            x2, y2 = to_node
            dx, dy = x2 - x1, y2 - y1

            direction = None
            if dx == -1:
                direction = "up"
            elif dx == 1:
                direction = "down"
            elif dy == -1:
                direction = "left"
            elif dy == 1:
                direction = "right"

            if direction:
                current_pheromone = grid[x1][y1]["pheromones"].get(direction, 0)
                grid[x1][y1]["pheromones"][direction] = current_pheromone + Q / self.cost

    def choose_move(self, grid: list[list[dict]]) -> None:
        if self.reached_goal:
            return False

        neighbors = self.get_neighbors(grid)
        if not neighbors:
            print(f"No valid moves from {self.cur_position}.")
            return False

        probs = self.neighbors_probabilities(neighbors, grid)
        next_pos = random.choices(neighbors, weights=probs)[0]
        self.move(next_pos, grid)
        return True
    
    

    def run(self, grid: list[list[dict]]) -> None:
        """
        Método para iniciar o movimento da formiga.
        Deve ser chamado após a inicialização da formiga.
        """

        i = 0
        keep_going = True
        while keep_going:
            i += 1
            keep_going = self.choose_move(grid=grid)
    
        return self.cost
            # print(f"Step {i}: Ant at {self.cur_position}, visited: {self.visited_nodes}")

    def __str__(self) -> str:
        return f"Ant at {self.cur_position}, visited: {self.visited_nodes}, tour length: {self.cost}"
