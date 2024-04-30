import math
import random

from threading import Thread


class Ant(Thread):
    def __init__(
        self,
        nodes,
        pheromoneMap,
        tmpPheromoneMap,
        first_pass,
        start,
        distance_callback,
        alpha,
        beta,
        pheromone_constant,
        pheromone_evaporation_rate,
        agent_index,
    ):
        Thread.__init__(self)

        self.nodes = nodes
        self.pheromoneMap = pheromoneMap
        self.tmpPheromoneMap = tmpPheromoneMap
        self.alpha = alpha
        self.beta = beta
        self.pheromone_constant = pheromone_constant
        self.pheromone_evaporation_rate = pheromone_evaporation_rate
        self.initialNode = start
        self.agent_index = agent_index
        self.distance = distance_callback

        self.first_pass = first_pass

    def run(self):
        self.trip = [self.initialNode]
        self.trip_distance = 0
        self.currentNode = self.initialNode

        while True:
            next_path = self.choose_next()


            if next_path[0] == self.currentNode:
                self.currentNode = next_path[1]
            else:
                self.currentNode = next_path[0]

            self.trip.append(self.currentNode)
            self.trip_distance += self.distance(next_path)


            # trip completion condition
            if self.trip[0] == self.trip[-1]:
                if len(self.trip) != 1:
                    self.pheromone_update()
                    return

    def choose_next(self):

        possible_nodes = []
        weightage_array = []

        most_probable = ((), 0)

        for path in self.pheromoneMap:

            if self.currentNode not in path:
                continue

            if path[0] == self.currentNode:
                next_node = path[1]
            else:
                next_node = path[0]

            if next_node in self.trip:
                if next_node == self.initialNode:
                    if len(self.trip) == len(self.nodes):
                        possible_nodes.append(path)

                continue

            possible_nodes.append(path)

        # 50% probablity on first pass
        if self.first_pass:
            choice = random.choice(possible_nodes)
            return choice

        for path in possible_nodes:
            path_distance = self.distance(path)
            # pheromone = self.pheromoneMap[path]
            pheromone = self.pheromone_constant / path_distance

            # calculate weightage of path
            weightage = (pheromone**self.alpha) * ((1 / path_distance) ** self.beta)

            weightage_array.append(weightage)

        weightage_sum = sum(weightage_array)

        for i in range(len(possible_nodes)):
            path = possible_nodes[i]
            weightage = weightage_array[i]

            p = weightage / weightage_sum

            if p > most_probable[1]:
                most_probable = (path, p)

        return most_probable[0]

    def pheromone_update(self):
        for i in range(len(self.trip) - 1):
            path = (self.trip[i], self.trip[i + 1])

            if path not in self.pheromoneMap:
                path = path[::-1]

            self.tmpPheromoneMap[path] = (
                1 - self.pheromone_evaporation_rate
            ) * self.tmpPheromoneMap[path]

            self.tmpPheromoneMap[path] += self.pheromone_constant / self.trip_distance


class AntColony:
    antArray = []
    pheromoneMap = {}
    tmpPheromoneMap = {}

    def __init__(
        self,
        nodes,
        start=None,
        ant_count=300,
        alpha=0.5,
        beta=1.2,
        pheromone_evaporation_rate=0.40,
        pheromone_constant=1000.0,
        iterations=300,
    ):

        self.nodes = nodes
        self.pheromone_evaporation_rate = pheromone_evaporation_rate
        self.pheromone_constant = pheromone_constant
        self.iterations = iterations
        self.alpha = alpha
        self.beta = beta
        self.first_pass = True
        self.ant_count = ant_count

        self.bestSeenPath = []
        self.bestDistance = None

        self.distanceArray = []

        if start:
            self.start = start
        else:
            self.start = random.choice(nodes)

        # Initialize Pheromone map
        self.init_pheromone_map()

        for iter in range(self.iterations):
            print("iteration: ", iter + 1)

            # Create all ants
            for i in range(self.ant_count):
                if not self.first_pass:
                    self.antArray.pop(i)
                ant = self.init_ant(i)
                self.antArray.append(ant)
                ant.start()

            for ant in self.antArray:
                ant.join()

                if not self.bestDistance:
                    self.bestDistance = ant.trip_distance

                if ant.trip_distance <= self.bestDistance:
                    self.bestDistance = ant.trip_distance
                    self.bestSeenPath = ant.trip

            for path in self.pheromoneMap:

                self.pheromoneMap[path] += self.tmpPheromoneMap[path]
                self.tmpPheromoneMap[path] = 0

            if self.first_pass:
                self.first_pass = False

    def init_ant(self, agent_index):
        return Ant(
            self.nodes,
            self.pheromoneMap,
            self.tmpPheromoneMap,
            self.first_pass,
            self.start,
            self.distance,
            self.alpha,
            self.beta,
            self.pheromone_constant,
            self.pheromone_evaporation_rate,
            agent_index,
        )

    def distance(self, path):
        (c1, c2) = path
        dx = c1[0] - c2[0]
        dy = c1[1] - c2[1]
        dist = math.sqrt(dx**2 + dy**2)
        return dist

    def init_pheromone_map(self):
        all_paths = []
        for i in self.nodes:
            for j in self.nodes:
                if i is j:
                    continue
                elif ((i, j) in all_paths) or ((j, i) in all_paths):
                    continue

                all_paths.append((i, j))

                self.pheromoneMap[(i, j)] = 0
                self.tmpPheromoneMap[(i, j)] = 0

    def get_path(self):
        print(self.bestDistance)
        return self.bestSeenPath
