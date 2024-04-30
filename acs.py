import numpy as np
from config import filename, iterations, num_ants, alpha, beta, rho, q, evaporation_rate
import sys

class ACS:
    def __init__(self, filename):
        self.filename = filename
        self.graph = self.load_graph()

    def load_graph(self):
        # Load the benchmark data from the file
        with open(self.filename, 'r') as file:
            lines = file.readlines()

        start_index = lines.index("NODE_COORD_SECTION\n")
        lines = lines[start_index + 1:]

        num_nodes = 0
        node_coords = {}
        for line in lines:
            if line.strip() == "EOF":
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

    def ant_colony_optimization(self, num_ants=num_ants, iterations=iterations, evaporation_rate=evaporation_rate, alpha=alpha, beta=beta):
        num_nodes = len(self.graph)
        pheromones = np.ones((num_nodes, num_nodes))  # Initial pheromone levels

        best_tour = None
        best_distance = float('inf')

        for iteration in range(iterations):
            ant_tours = []
            ant_distances = []

            for ant in range(num_ants):
                current_node = np.random.randint(num_nodes)
                visited_nodes = [current_node]
                tour_distance = 0.0

                while len(visited_nodes) < num_nodes:
                    unvisited_nodes = [node for node in range(num_nodes) if node not in visited_nodes]
                    probabilities = []
                    for next_node in unvisited_nodes:
                        if self.graph[current_node][next_node] == 0:
                            # Avoid division by zero by setting probability to 0 for zero-distance edges
                            probabilities.append(0.0)
                        else:
                            probabilities.append(((pheromones[current_node][next_node] ** alpha) *
                                (1.0 / self.graph[current_node][next_node]) ** beta))

                    # Check if all probabilities are zero
                    if all(prob == 0 for prob in probabilities):
                        # Set equal probabilities for unvisited nodes
                        probabilities = [1.0 / len(unvisited_nodes) for _ in unvisited_nodes]
                    else:
                        probabilities = np.array(probabilities) / np.sum(probabilities)

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



    def print_results(self, best_tour, best_distance):
        with open(self.filename, 'r') as file:
            lines = file.readlines()

        name = None
        dimension = None
        comment = None

        for line in lines:
            if line.startswith("NAME"):
                name = line.split(":")[1].strip()
            elif line.startswith("DIMENSION"):
                dimension = line.split(":")[1].strip()
            elif line.startswith("COMMENT"):
                comment = line.split(":")[1].strip()

        if name:
            print(f"NAME : {name}")
        if comment:
            print(f"COMMENT : {comment}")
        if dimension:
            print(f"DIMENSION : {dimension}")

        print(f"Best tour: {best_tour}")
        print(f"Best distance: {best_distance}")

# Example usage:
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python pacs.py <filename>")
        sys.exit(1)

    filename = sys.argv[1]

acs_solver = ACS(filename)
best_tour, best_distance = acs_solver.ant_colony_optimization()
acs_solver.print_results(best_tour, best_distance)
