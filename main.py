import sys
from src.environment import Environment
"""
============ PSEUDOCODIGO ACO ============

Initialize pheromone trails τ on all edges to a small positive value
Set ACO parameters: number_of_ants, number_of_iterations, α, β, ρ, Q

for iteration = 1 to number_of_iterations do
    for each ant k = 1 to number_of_ants do
        Place ant k on a randomly chosen start node
        Initialize tabu list for ant k to keep track of visited nodes

        while ant k has not visited all nodes do
            Select next node j for ant k based on probability:
                P_ij ∝ (τ_ij)^α * (η_ij)^β
                where:
                    - τ_ij is the pheromone on edge (i,j)
                    - η_ij is the heuristic value (e.g., 1/distance)
                    - α controls pheromone influence
                    - β controls heuristic influence
            Move ant k to node j
            Add node j to tabu list

        Complete the tour and compute total cost for ant k

    Update pheromones on all edges:
        For each edge (i,j):
            Evaporate pheromone: τ_ij ← (1 - ρ) * τ_ij
            For each ant k that used edge (i,j) in its tour:
                τ_ij ← τ_ij + Δτ_ij^k
                where:
                    Δτ_ij^k = Q / L_k
                    L_k is the tour length of ant k
                    Q is a constant

    Optionally: keep track of the best tour found so far

Return the best tour found

======================================================


Serial = Parallel with 1 process !
"""

def main():
    NUM_PROCESS = int(sys.argv[-1]) if len(sys.argv) > 1 else 1 
    print(NUM_PROCESS)

    GRID_SCALE = (50, 50)
    NUM_ANTS = 500
    NUM_ITERATIONS = 500
    GOAL = (25, 25)

    env = Environment(
            number_cols=GRID_SCALE[0], 
            number_rows=GRID_SCALE[1], 
            number_ants=NUM_ANTS, 
            number_process=NUM_PROCESS,
            number_obstacles=1, 
            number_iterations=NUM_ITERATIONS, 
            goalx=GOAL[0], 
            goaly=GOAL[1],
            load_grid=False
        )
    if(NUM_PROCESS == 1):
        env.optimize()
    else:
        env.optimize_mp_pipes_n_queues()

if __name__ == "__main__":
    main()


