
"""
============ PSEUDOCODIGO ACO da Wikipedia ============

procedure ACO_MetaHeuristic is
    while not terminated do
        generateSolutions()
        daemonActions()
        pheromoneUpdate()
    repeat
end procedure

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

import random


def ACO_MetaHeuristic():
    while not terminated:
        generateSolutions()
        daemonActions()
        pheromoneUpdate()
    pass



def generateSolutions():
    # Implement the logic to generate solutions based on pheromone trails
    pass
def daemonActions():
    # Implement the logic for daemon actions, such as updating global best solutions
    pass
def pheromoneUpdate():
    # Implement the logic to update pheromone trails based on the solutions generated
    pass





lons = range(-180, 180)
lats = range(-90, 90)
target_lat = random.randint(-90, 90)
target_lon = random.randint(-180, 180)
target = (target_lon, target_lat)

terra_cartesiano = []
for lon in lons:
    for lat in lats:
        terra_cartesiano.append((lon, lat))
# Print the generated Cartesian coordinates of the Earth


print(terra_cartesiano)  



