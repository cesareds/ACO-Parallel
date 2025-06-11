import cupy as cp

class Ant:
    def __init__(self, start, goal, alpha, beta, number_cols, number_rows):
        self.start = start
        self.goal = goal
        self.alpha = alpha
        self.beta = beta
        self.number_cols = number_cols
        self.number_rows = number_rows
        self.reset()

    def reset(self):
        self.position = self.start
        self.visited_nodes = [self.position]
        self.cost = 0.0
        self.reached_goal = False

    def run(self, grid_values, pheromones):
        while not self.reached_goal:
            moves = self.get_valid_moves(grid_values)
            if not moves:
                break
            probs = self.calculate_probabilities(moves, pheromones)
            next_move = self.select_move(moves, probs)
            self.move(next_move)

            if self.position == self.goal:
                self.reached_goal = True

    def get_valid_moves(self, grid_values):
        directions = {
            "up":    (-1, 0, 0),
            "down":  (1, 0, 1),
            "left":  (0, -1, 2),
            "right": (0, 1, 3)
        }

        valid_moves = []
        x, y = self.position

        for name, (dx, dy, dir_idx) in directions.items():
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.number_rows and 0 <= ny < self.number_cols:
                if grid_values[nx, ny] != -1 and (nx, ny) not in self.visited_nodes:
                    valid_moves.append(((nx, ny), dir_idx))
        return valid_moves

    def calculate_probabilities(self, moves, pheromones):
        x, y = self.position
        probs = []
        total = cp.float32(0.0)

        for (nx, ny), dir_idx in moves:
            pheromone = pheromones[x, y, dir_idx]
            heuristic = 1.0 / (cp.linalg.norm(cp.array([nx - self.goal[0], ny - self.goal[1]])) + 1e-6)
            val = (pheromone ** self.alpha) * (heuristic ** self.beta)
            probs.append(val)
            total += val

        return cp.array(probs) / (total + 1e-10)

    def select_move(self, moves, probabilities):
        idx = cp.random.choice(cp.arange(len(moves)), p=probabilities).item()
        return moves[idx]

    def move(self, move):
        new_position, _ = move
        self.visited_nodes.append(new_position)
        self.cost += 1.0
        self.position = new_position

    def update_pheromone(self, pheromones, Q=1.0):
        for i in range(len(self.visited_nodes) - 1):
            x1, y1 = self.visited_nodes[i]
            x2, y2 = self.visited_nodes[i + 1]

            if x2 == x1 - 1 and y2 == y1:
                dir_idx = 0  # up
            elif x2 == x1 + 1 and y2 == y1:
                dir_idx = 1  # down
            elif x2 == x1 and y2 == y1 - 1:
                dir_idx = 2  # left
            elif x2 == x1 and y2 == y1 + 1:
                dir_idx = 3  # right
            else:
                continue

            pheromones[x1, y1, dir_idx] += Q / self.cost

    def __str__(self) -> str:
        return f"Ant at {self.position}, visited: {self.visited_nodes}, Cost: {self.cost}"
