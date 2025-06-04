import math
import random

class Ant:
    """
    Ants represent the drones from the original problem.
    Each ant has a current position, a list of visited nodes, and logic for movement and pheromone updates.
    """
    def __init__(self, start: tuple, goal: tuple, alpha: float, beta: float, number_cols: int, number_rows: int) -> None:
        self.goal           = goal
        self.start          = start
        self.cur_position   = (self.start[0], self.start[1])
        self.visited_nodes  = [self.cur_position]
        self.alpha          = alpha
        self.beta           = beta
        self.reached_goal   = False
        self.number_cols    = number_cols
        self.number_rows    = number_rows

    @property
    def cost(self) -> int:
        return len(self.visited_nodes)

    def manhattan_distance(self, x1, y1, x2, y2) -> int:
        dx = min(abs(x1 - x2), self.number_rows - abs(x1 - x2))
        dy = min(abs(y1 - y2), self.number_cols - abs(y1 - y2))
        return dx + dy

    def reset(self) -> None:
        self.cur_position   = (self.start[0], self.start[1])
        self.visited_nodes  = [self.cur_position]
        self.reached_goal   = False 

    def get_direction(self, from_pos: tuple, to_pos: tuple):
        x1, y1 = from_pos
        x2, y2 = to_pos

        if (x1 - x2) % self.number_rows == 1:
            return "up"
        elif (x2 - x1) % self.number_rows == 1:
            return "down"
        elif (y1 - y2) % self.number_cols == 1:
            return "left"
        elif (y2 - y1) % self.number_cols == 1:
            return "right"
        return None

    def get_pheromone(self, from_pos: tuple, to_pos: tuple, grid: list[list[dict]]) -> float:
        x1, y1 = from_pos
        x2, y2 = to_pos
        
        direction = self.get_direction(from_pos, to_pos)

        if direction:
            return grid[x1][y1]["pheromones"].get(direction, 1e-6)
        return 1e-6  # invalid movement

    def neighbors_probabilities(self, allowed_nodes: list[tuple], grid: list[list[dict]]) -> list[float]:
        probabilities = []
        denominator = 0.0

        for node in allowed_nodes:
            tau = self.get_pheromone(self.cur_position, node, grid)
            eta = 1 / (self.manhattan_distance(self.cur_position[0], self.cur_position[1], node[0], node[1]))   
            prob = (tau ** self.alpha) * (eta ** self.beta)

            probabilities.append(prob)
            denominator += prob

        if denominator == 0:
            return [1 / len(allowed_nodes)] * len(allowed_nodes)

        return [p / denominator for p in probabilities]

    def move(self, next_position: tuple, grid: list[list[dict]]) -> None:
        # Update current position and check if goal was reached
        self.cur_position = next_position
        self.visited_nodes.append(next_position)

        x, y = next_position
        if grid[x][y]["value"] == 1:
            self.reached_goal = True

    def get_neighbors(self, grid: list[list[dict]]) -> list[tuple]:
        # Get all valid neighbor positions that are not obstacles or already visited
        x, y = self.cur_position
        neighbors = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for dx, dy in directions:
            new_x, new_y = x + dx, y + dy

            # Apply wrapping (toroidal grid)
            if new_x < 0:
                new_x = self.number_rows - 1
            elif new_x >= self.number_rows:
                new_x = 0
            if new_y < 0:
                new_y = self.number_cols - 1
            elif new_y >= self.number_cols:
                new_y = 0

            if grid[new_x][new_y]["value"] >= 0 and (new_x, new_y) not in self.visited_nodes:
                neighbors.append((new_x, new_y))

        return neighbors

    def update_pheromone(self, grid: list[list[dict]], Q: float) -> None:
        """
        Updates the pheromone levels on the edges traversed by the ant.
        :param grid: the environment grid
        :param Q: pheromone deposit constant
        """
        for i in range(len(self.visited_nodes) - 1):
            from_node = self.visited_nodes[i]
            to_node = self.visited_nodes[i + 1]

            x1, y1 = from_node
            x2, y2 = to_node

            dx = (x2 - x1) % self.number_rows
            dy = (y2 - y1) % self.number_cols

            if dx == 1 or dx == -(self.number_rows - 1):
                direction = "down"
            elif dx == self.number_rows - 1 or dx == -1:
                direction = "up"
            elif dy == 1 or dy == -(self.number_cols - 1):
                direction = "right"
            elif dy == self.number_cols - 1 or dy == -1:
                direction = "left"
            else:
                direction = None

            if direction:
                current_pheromone = grid[x1][y1]["pheromones"].get(direction, 0)
                grid[x1][y1]["pheromones"][direction] = current_pheromone + Q / self.cost

    def choose_move(self, grid: list[list[dict]]) -> bool:
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

    def run(self, grid: list[list[dict]]) -> int:
        """
        Executes the ant's movement through the environment.
        Should be called after initialization or reset.
        """
        step = 0
        keep_going = True
        while keep_going:
            step += 1
            keep_going = self.choose_move(grid=grid)
    
        return self.cost

    def __str__(self) -> str:
        return f"Ant at {self.cur_position}, visited: {self.visited_nodes}, tour length: {self.cost}"
