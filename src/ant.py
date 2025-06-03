class Ant:
    """
    The drones from the original problem are represented as ants.
    Each ant has a current position, a list of visited nodes, and a tabu list.
    """
    def __init__(self, start: tuple, alpha: float, beta: float) -> None:
        """
        Start node position = (0, 0)
        Goal node position = (M, N)
        """
        self.cur_position   = (start[0], start[1])
        self.visited_nodes  = [self.cur_position]
        self.tabu_list      = [] # Avoid visiting the same node twice
        self.tour_length    = 0  # Total cost of the tour (how many nodes visited)
        self.alpha          = alpha
        self.beta           = beta

    def neighbors_probabilities(
                self,
                allowed_nodes: list[tuple],
                pheromone_matrix: dict,
                alpha: float
            ) -> list[float]:
        """
        Calculates the probability of moving to each allowed neighboring node,
        based only on the pheromone level, since the heuristic value is constant.

        Parameters:
        - allowed_nodes: list of neighboring coordinates [(x1, y1), (x2, y2), ...]
        - pheromone_matrix: dictionary of the form {(from_node, to_node): τ_ij}
        - alpha: the influence factor of the pheromone

        Returns:
        - A list of probabilities corresponding to each allowed node.
        """

        probabilities = []
        denominator = 0.0

        for node in allowed_nodes:
            # Minimum values if there is no pheromone
            tau = pheromone_matrix.get((self.cur_position, node), 1e-6)  
            prob = (tau ** alpha)
            probabilities.append(prob)
            denominator += prob

        if denominator == 0:
            # Avoids division by zero: returns uniform distribution
            return [1 / len(allowed_nodes)] * len(allowed_nodes)

        probabilities = [p / denominator for p in probabilities]
        return probabilities

            
        
    def move(self, next_position: tuple) -> None:
        pass
    
    def reset(self) -> None:
        """
        Reset the ant's state for a new tour.
        """
        self.cur_position   = (0, 0)
        self.visited_nodes  = [self.cur_position]
        self.tabu_list      = []
        self.tour_length    = 0
        
        
    def __str__(self) -> str:
        return f"Ant at {self.cur_position}, visited: {self.visited_nodes}, tabu: {self.tabu_list}, tour length: {self.tour_length}"