import numpy as np

class PACS_ACO:
    def __init__(self, filename):
        self.filename = filename
        self.graph = self.load_graph()
        self.search_tsp_info()

    def search_tsp_info(self):
        with open(self.filename, 'r') as file:
            for line in file:
                if line.startswith("NAME :") or line.startswith("COMMENT :") or line.startswith("DIMENSION :"):
                    print(line.strip())

    def load_graph(self):
        # Load the benchmark data from the file
        with open(self.filename, 'r') as file:
            lines = file.readlines()

        start_index = lines.index("NODE_COORD_SECTION\n")
        lines = lines[start_index + 1:]

        num_nodes = 0
        node_coords = {}
        for line in lines:
            if not line.strip():  # Check for empty line
                break
            parts = line.split()
            if len(parts) < 3:  # Skip lines without coordinates
                continue
            node_index = int(parts[0]) - 1  # Adjust for 0-based indexing
            x_coord = float(parts[1])
            y_coord = float(parts[2])
            node_coords[node_index] = (x_coord, y_coord)
            num_nodes += 1

        graph = np.zeros((num_nodes, num_nodes))
        for i in range(num_nodes):
            for j in range(num_nodes):
                if i != j:
                    x1, y1 = node_coords[i]
                    x2, y2 = node_coords[j]
                    distance = np.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
                    graph[i][j] = distance
                    graph[j][i] = distance  # Assuming symmetric TSP

        return graph

    def partial_ant_colony_system(self, num_ants=10, max_iterations=100, evaporation_rate=0.5, alpha=1.0, beta=2.0):
        num_nodes = len(self.graph)
        pheromones = np.ones((num_nodes, num_nodes))  # Initial pheromone levels

        best_tour = None
        best_distance = float('inf')

        for iteration in range(max_iterations):
            ant_tours = []
            ant_distances = []

            for ant in range(num_ants):
                current_node = np.random.randint(num_nodes)
                visited_nodes = [current_node]
                tour_distance = 0.0

                while len(visited_nodes) < num_nodes:
                    unvisited_nodes = [node for node in range(num_nodes) if node not in visited_nodes]
                    probabilities = [((pheromones[current_node][next_node] ** alpha) *
                                      (1.0 / self.graph[current_node][next_node]) ** beta)
                                    for next_node in unvisited_nodes]

                    # Check for zero probabilities
                    sum_probabilities = np.sum(probabilities)
                    if sum_probabilities == 0:
                        selected_node = np.random.choice(unvisited_nodes)
                    else:
                        epsilon = 1e-9  # Small epsilon value to avoid division by zero
                        probabilities /= (sum_probabilities + epsilon)  # Normalize probabilities

                        # Corrective adjustment to ensure probabilities sum to 1
                        diff_sum = 1.0 - np.sum(probabilities)
                        probabilities[-1] += diff_sum  # Add the difference to the last probability

                        selected_node = np.random.choice(unvisited_nodes, p=probabilities)

                    visited_nodes.append(selected_node)
                    tour_distance += self.graph[current_node][selected_node]
                    current_node = selected_node

                tour_distance += self.graph[visited_nodes[-1]][visited_nodes[0]]  # Return to start node
                ant_tours.append(visited_nodes)
                ant_distances.append(tour_distance)

                if tour_distance < best_distance:
                    best_tour = visited_nodes
                    best_distance = tour_distance

            # Update pheromone levels
            pheromones *= (1 - evaporation_rate)
            for ant, tour in enumerate(ant_tours):
                for i in range(len(tour) - 1):
                    pheromones[tour[i]][tour[i + 1]] += 1.0 / ant_distances[ant]
                pheromones[tour[-1]][tour[0]] += 1.0 / ant_distances[ant]

        return best_tour, best_distance

# Example usage:
filename = "US.tsp"  # Replace with the actual filename
pacs_solver = PACS_ACO(filename)
best_tour, best_distance = pacs_solver.partial_ant_colony_system()
print("Best tour:", best_tour)
print("Best distance:", best_distance)
