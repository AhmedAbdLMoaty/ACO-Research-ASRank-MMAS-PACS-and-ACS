import random
import math
from racs import RACS

filename = 'US.tsp'

class City:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y

    def distance(self, other):
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

class ACO:
    def __init__(self, cities, num_ants, alpha, beta, rho, pheromone_init):
        self.cities = cities
        self.num_ants = num_ants
        self.alpha = alpha
        self.beta = beta
        self.rho = rho
        self.pheromone = [[pheromone_init for _ in range(len(cities))] for _ in range(len(cities))]
        self.best_distance = float('inf')
        self.best_tour = []

    def _calculate_heuristic(self, i, j):
        return 1 / self.cities[i].distance(self.cities[j])

    def _choose_next_city(self, ant, visited):
        probabilities = [0.0 for _ in range(len(self.cities))]
        total = 0.0
        for next_city in range(len(self.cities)):
            if next_city not in visited:
                heuristic = self._calculate_heuristic(ant.current_city, next_city)
                probability = self.pheromone[ant.current_city][next_city] ** self.alpha * heuristic ** self.beta
                total += probability
                probabilities[next_city] = probability
        if total == 0.0:
            return random.choice([city for city in range(len(self.cities)) if city not in visited])
        return random.choices(range(len(self.cities)), weights=probabilities)[0]

    def _update_pheromone(self, tour, distance):
        for i in range(1, len(tour)):
            self.pheromone[tour[i - 1]][tour[i]] = (1 - self.rho) * self.pheromone[tour[i - 1]][tour[i]] + self.rho / distance

    def run(self, iterations):
        for _ in range(iterations):
            ants = [Ant(self.cities) for _ in range(self.num_ants)]
            for ant in ants:
                for _ in range(len(self.cities) - 1):
                    next_city = self._choose_next_city(ant, ant.visited)
                    ant.visit_city(next_city)
                ant.visit_city(ant.start_city)  # Complete the tour
            shortest_ant = min(ants, key=lambda ant: ant.total_distance)
            self.best_distance = shortest_ant.total_distance
            self.best_tour = shortest_ant.tour
            self._update_pheromone(self.best_tour, self.best_distance)

    def get_shortest_tour(self):
        return self.best_tour, self.best_distance

class Ant:
    def __init__(self, cities):
        self.cities = cities
        self.start_city = random.randint(0, len(cities) - 1)
        self.current_city = self.start_city
        self.visited = {self.start_city}
        self.tour = [self.start_city]
        self.total_distance = 0.0

    def visit_city(self, city):
        self.visited.add(city)
        self.tour.append(city)
        self.total_distance += self.cities[self.current_city].distance(self.cities[city])
        self.current_city = city

class ACS(ACO):
    pass

class MMAS(ACO):
    def __init__(self, cities, num_ants, alpha, beta, rho, pheromone_init, tau_min, tau_max):
        super().__init__(cities, num_ants, alpha, beta, rho, pheromone_init)
        self.tau_min = tau_min
        self.tau_max = tau_max

    def _update_pheromone(self, tour, distance):
        for i in range(1, len(tour)):
            delta_tau = int(math.ceil(1 / distance))
            self.pheromone[tour[i - 1]][tour[i]] = min(self.tau_max, max(self.tau_min, (1 - self.rho) * self.pheromone[tour[i - 1]][tour[i]] + self.rho * delta_tau))

class RACS:
    def __init__(self, cities, num_ants, alpha, beta, rho, q):
        self.cities = cities
        self.num_ants = num_ants
        self.alpha = alpha
        self.beta = beta
        self.rho = rho
        self.q = q
        self.pheromone = [[1.0 for _ in range(len(cities))] for _ in range(len(cities))]  # Initialize pheromone levels

    def update_pheromone(self, tours):
        # Placeholder method for updating pheromone levels based on ant tours
        pass

    def run(self, iterations):
        for _ in range(iterations):
            ants = [Ant(self.cities) for _ in range(self.num_ants)]
            for ant in ants:
                ant.make_tour()

            # Sort ants by tour length
            ants.sort(key=lambda x: x.total_distance)

            # Select elite ants
            elite_ants = ants[:int(self.q * self.num_ants)]

            # Update pheromone levels based on elite ant tours
            self.update_pheromone([ant.tour for ant in elite_ants])

        # Find the best tour among elite ants
        best_tour = min(elite_ants, key=lambda x: x.total_distance).tour
        best_distance = min(elite_ants, key=lambda x: x.total_distance).total_distance

        return best_tour, best_distance


    def _update_pheromone(self, tour, distance):
        for i in range(1, len(tour)):
            if distance != 0:
                delta_tau = 1 / distance
                self.pheromone[tour[i - 1]][tour[i]] += delta_tau




    def get_shortest_tour(self):
        return super().get_shortest_tour()

class PACS(ACO):
    pass

def parse_tsp_file(filename):
    cities = []
    with open(filename, 'r') as file:
        lines = file.readlines()
        section_found = False
        print(f"Algorithm: {aco_type}")
        for line in lines:
                if line.startswith('NODE_COORD_SECTION'):
                    section_found = True
                    break
                elif line.startswith('COMMENT :'):
                    print(f"Comment found: {line.strip()}")  # Print comment lines
                elif line.startswith('NAME :'):
                    print(f"Problem name: {line.strip().split(':')[1].strip()}")
                elif line.startswith('DIMENSION :'):
                    dimension = int(line.strip().split(':')[1].strip())
                    print(f"Number of cities: {dimension}")

        if not section_found:
            raise ValueError("NODE_COORD_SECTION not found in the TSP file.")

        for line in lines:
            if line.strip() == 'EOF':
                break
            city_info = line.split()
            if len(city_info) != 3:
                continue  # Skip lines that don't have three columns (ID, X, Y)
            try:
                city_id = int(city_info[0])
                x_coord = float(city_info[1])
                y_coord = float(city_info[2])
                cities.append(City(city_id, x_coord, y_coord))
            except ValueError:
                continue
        if dimension is not None and len(cities) != dimension:
            print(f"Warning: Number of cities ({len(cities)}) does not match dimension ({dimension})")
    return cities




def run_tsp_from_file(filename, iterations, num_ants, aco_type):
    cities = parse_tsp_file(filename)
    if aco_type == "ACS":
        aco = ACS(cities, num_ants, 1.0, 1.0, 0.1, 1.0)
    elif aco_type == "MMAS":
        aco = MMAS(cities, num_ants, 1.0, 1.0, 0.1, 1.0, 0.001, 10.0)
    elif aco_type == "RACS":
        aco = RACS(cities, num_ants, 1.0, 1.0, 0.1, 0.1) 
    elif aco_type == "PACS":
        aco = PACS(cities, num_ants, 1.0, 1.0, 0.1, 1.0)  # Same parameters as ACS for this example
    else:
        raise ValueError("Invalid ACO type")

    aco.run(iterations)
    best_tour, best_distance = aco.get_shortest_tour()
    return best_tour, best_distance


iterations = 100
num_ants = 25
aco_types = ["ACS", "MMAS", "PACS"]  # List of ACO algorithms

for aco_type in aco_types:
    best_tour, best_distance = run_tsp_from_file(filename, iterations, num_ants, aco_type)
    print("Best Tour:", best_tour)
    print("Best Distance:", best_distance)
    print("-" * 50)