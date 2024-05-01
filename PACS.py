import numpy as np
import sys
from config import iterations, num_ants, alpha, beta, rho, q, evaporation_rate


class PACS_ACO:
    def __init__(self, filename):
        self.filename = filename
        self.graph = self.load_graph()
        self.dimension = self.search_tsp_info()

    def search_tsp_info(self):
        dimension = None
        with open(self.filename, 'r') as file:
            for line in file:
                line = line.strip().lower()  # Convert line to lowercase and remove leading/trailing spaces
                if line.startswith(("name:", "comment:", "dimension:")):
                    line_parts = line.split(":")
                    if len(line_parts) > 1:
                        key = line_parts[0].strip()
                        value = line_parts[1].strip()
                        print(f"{key.capitalize()} : {value}")
                        if key == "dimension":
                            dimension = int(value)
                    else:
                        print(line)
        return dimension

    def load_graph(self):
        with open(self.filename, 'r') as file:
            lines = file.readlines()

        # Debug: Print the first few lines of the file
        print("First few lines of the file:")
        for line in lines[:5]:  # Print the first 5 lines
            print(line.strip())

        # Find the index of the line containing "NODE_COORD_SECTION"
        start_index = -1
        for idx, line in enumerate(lines):
            if line.startswith("NODE_COORD_SECTION"):
                start_index = idx
                break

        # Debug: Print the start index and the line at that index
        print("Start index of 'NODE_COORD_SECTION':", start_index)
        if start_index != -1:
            print("Line at start index:", lines[start_index].strip())

        if start_index == -1:
            raise ValueError("Missing 'NODE_COORD_SECTION' marker in the file.")

        lines = lines[start_index + 1:]

        num_nodes = 0
        node_coords = {}
        for line in lines:
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

    def partial_ant_colony_system(self, num_ants=num_ants, max_iterations=iterations, evaporation_rate=evaporation_rate, alpha=alpha, beta=beta):
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
                                      (1.0 / max(self.graph[current_node][next_node], 1e-9)) ** beta)
                                    for next_node in unvisited_nodes]

                    # Normalize probabilities
                    sum_probabilities = np.sum(probabilities)
                    if sum_probabilities != 0:
                        probabilities /= sum_probabilities
                    else:
                        probabilities = np.ones(len(unvisited_nodes)) / len(unvisited_nodes)  # Equal probabilities if sum is 0

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

            pheromones *= (1 - evaporation_rate)
            for ant, tour in enumerate(ant_tours):
                for i in range(len(tour) - 1):
                    pheromones[tour[i]][tour[i + 1]] += 1.0 / max(ant_distances[ant], 1e-9)
                pheromones[tour[-1]][tour[0]] += 1.0 / max(ant_distances[ant], 1e-9)

        return best_tour, best_distance


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python pacs.py <filename>")
        sys.exit(1)

    filename = sys.argv[1]
    pacs_solver = PACS_ACO(filename)
    best_tour, best_distance = pacs_solver.partial_ant_colony_system()
    print("Best tour:", best_tour)
    print("Best distance:", best_distance)
