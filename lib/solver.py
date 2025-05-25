import random
from typing import List, Dict
from lib.data_structures import Point, Vehicle


class GeneticAlgorithmVRP:
    """
    Genetic Algorithm for Vehicle Routing Problem with multiple vehicle types.

    Attributes:
        points (List[Point]): List of delivery points (first point is warehouse by default)
        vehicle_types (List[Dict]): List of vehicle type specifications (each dict with keys: capacity, count)
        population_size (int): Number of individuals in population
        generations (int): Number of generations to run
        mutation_rate (float): Probability of mutation
        elite_size (int): Number of best individuals to preserve
        tournament_size (int): Size of tournament for selection
    """

    def __init__(
        self,
        points: List[Point],
        vehicle_types: List[Dict],
        population_size: int = 100,
        generations: int = 100,
        mutation_rate: float = 0.1,
        elite_size: int = 10,
        tournament_size: int = 3,
    ):
        self.points = points
        self.vehicle_types = vehicle_types
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.elite_size = elite_size
        self.tournament_size = tournament_size
        self.warehouse = points[0]

        # Validate vehicle types
        if not all('capacity' in vt and 'count' in vt for vt in self.vehicle_types):
            raise ValueError("Each vehicle type must have 'capacity' and 'count'")

    def create_individual(self) -> List[Point]:
        """Creates a random individual (a permutation of delivery points excluding warehouse)."""
        return random.sample(self.points[1:], len(self.points) - 1)

    def initialize_population(self) -> List[List[Point]]:
        """Initializes population."""
        return [self.create_individual() for _ in range(self.population_size)]

    def fitness(self, individual: List[Point]) -> float:
        """Calculates total distance of delivery plan. Lower is better."""
        try:
            vehicles = self.create_delivery_plan(individual)
            total_distance = sum(v.total_distance for v in vehicles)
            return total_distance
        except Exception:
            return float('inf')

    def tournament_selection(self, population: List[List[Point]]) -> List[Point]:
        """Selects an individual via tournament selection."""
        candidates = random.sample(population, self.tournament_size)
        best = min(candidates, key=self.fitness)
        return best.copy()

    def ordered_crossover(self, parent1: List[Point], parent2: List[Point]) -> List[Point]:
        """Ordered crossover preserving gene order."""
        size = len(parent1)
        start, end = sorted(random.sample(range(size), 2))

        child = [None] * size
        child[start:end + 1] = parent1[start:end + 1]

        parent2_idx = 0
        for i in range(size):
            if child[i] is None:
                while parent2[parent2_idx] in child:
                    parent2_idx += 1
                child[i] = parent2[parent2_idx]
                parent2_idx += 1

        return child

    def mutate(self, individual: List[Point]) -> List[Point]:
        """Swap mutation."""
        if random.random() < self.mutation_rate:
            i, j = random.sample(range(len(individual)), 2)
            individual[i], individual[j] = individual[j], individual[i]
        return individual

    def create_delivery_plan(self, individual: List[Point]) -> List[Vehicle]:
        for p in self.points[1:]:
            p.remaining_demand = p.total_demand.copy()

        vehicles = []
        vehicle_id = 1
        for vt in self.vehicle_types:
            for _ in range(vt['count']):
                v = Vehicle(vehicle_id, vt['type'])
                v.reset()
                v.add_stop(self.warehouse, is_warehouse=True)
                v.reload()
                vehicles.append(v)
                vehicle_id += 1

        for point in individual:
            while any(amount > 0 for amount in point.remaining_demand.values()):
                vehicle = self.select_vehicle(vehicles, point)
                if sum(vehicle.current_load.values()) == 0:
                    vehicle.add_stop(self.warehouse, is_warehouse=True)
                    vehicle.reload()

                delivery = {}
                remaining_capacity = sum(vehicle.current_load.values())
                for product, amount in point.remaining_demand.items():
                    deliver_qty = min(amount, vehicle.current_load[product])
                    delivery[product] = deliver_qty
                    remaining_capacity -= deliver_qty
                    point.remaining_demand[product] -= deliver_qty

                vehicle.add_stop(point, delivery)

        for v in vehicles:
            if not v.route or v.route[-1]["point"] != self.warehouse:
                v.add_stop(self.warehouse, is_warehouse=True)
            v.total_distance = 0
            last_point = self.warehouse
            for stop in v.route:
                current_point = stop["point"]
                v.total_distance += last_point.distance_to(current_point)
                last_point = current_point

        return vehicles

    def select_vehicle(self, vehicles: List[Vehicle], point: Point) -> Vehicle:
        """
        Selects the best vehicle to deliver to the given point.

        The selection tries to maximize efficiency = possible delivery / (travel cost + 1e-6)
        """
        best_vehicle = None
        best_efficiency = -1

        for vehicle in vehicles:
            current_pos = (
                self.warehouse if sum(vehicle.current_load.values()) == 0
                else vehicle.route[-1]["point"]
            )
            cost_to_point = current_pos.distance_to(point)
            cost_to_warehouse = point.distance_to(self.warehouse)
            total_cost = cost_to_point + cost_to_warehouse

            possible_delivery = sum(
                min(vehicle.current_load[prod], point.remaining_demand.get(prod, 0))
                for prod in vehicle.current_load
            )

            efficiency = possible_delivery / (total_cost + 1e-6)

            if possible_delivery > 0 and efficiency > best_efficiency:
                best_efficiency = efficiency
                best_vehicle = vehicle

        if best_vehicle is None:
            best_vehicle = min(
                vehicles,
                key=lambda v: v.route[-1]["point"].distance_to(self.warehouse) if v.route else float('inf')
            )

        return best_vehicle

    def run(self) -> List[Vehicle]:
        """Runs the genetic algorithm to solve the VRP."""
        population = self.initialize_population()

        for gen in range(self.generations):
            population = sorted(population, key=self.fitness)

            new_population = population[:self.elite_size]

            while len(new_population) < self.population_size:
                parent1 = self.tournament_selection(population)
                parent2 = self.tournament_selection(population)

                if random.random() < 0.7:
                    child = self.ordered_crossover(parent1, parent2)
                else:
                    child = self.ordered_crossover(parent1, parent2)

                child = self.mutate(child)

                new_population.append(child)

            population = new_population

        best_individual = min(population, key=self.fitness)
        best_vehicles = self.create_delivery_plan(best_individual)

        return best_vehicles
