import random
from typing import List, Dict, Set

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

        if not all('capacity' in vt and 'count' in vt for vt in self.vehicle_types):
            raise ValueError("Each vehicle type must have 'capacity' and 'count'")

    def create_individual(self) -> List[Point]:
        return random.sample(self.points[1:], len(self.points) - 1)

    def initialize_population(self) -> List[List[Point]]:
        return [self.create_individual() for _ in range(self.population_size)]

    def fitness(self, individual: List[Point]) -> float:
        try:
            vehicles = self.create_delivery_plan(individual)
            return sum(v.total_distance for v in vehicles)
        except Exception as e:
            print(f"Fitness calculation failed: {e}")
            return float('inf')

    def tournament_selection(self, population: List[List[Point]]) -> List[Point]:
        candidates = random.sample(population, self.tournament_size)
        return min(candidates, key=self.fitness).copy()

    def ordered_crossover(self, parent1: List[Point], parent2: List[Point]) -> List[Point]:
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
                v.capacity = vt['capacity']
                vehicles.append(v)
                vehicle_id += 1

        for vehicle in vehicles:
            # Jeśli pojazd nie odwiedził żadnego punktu poza magazynem, dodaj pustą trasę do/z magazynu
            if not vehicle.route:
                vehicle.add_stop(self.warehouse, is_warehouse=True)
                vehicle.reload()
                vehicle.add_stop(self.warehouse, is_warehouse=True)
                self._calculate_vehicle_distance(vehicle)
            elif vehicle.route[-1]["point"] != self.warehouse:
                vehicle.add_stop(self.warehouse, is_warehouse=True)
                self._calculate_vehicle_distance(vehicle)


        visited_points = set()

        for point in individual:
            self._ensure_point_fully_served(point, vehicles, visited_points)
            visited_points.add(point)

        unvisited = set(self.points[1:]) - visited_points
        if unvisited:
            raise RuntimeError(f"Points not visited: {[p.id for p in unvisited]}")

        for point in self.points[1:]:
            if any(demand > 0 for demand in point.remaining_demand.values()):
                raise RuntimeError(f"Point {point.id} has unsatisfied demands: {point.remaining_demand}")

        for vehicle in vehicles:
            if not vehicle.route or vehicle.route[-1]["point"] != self.warehouse:
                vehicle.add_stop(self.warehouse, is_warehouse=True)
            self._calculate_vehicle_distance(vehicle)

        return vehicles

    def _ensure_point_fully_served(self, point: Point, vehicles: List[Vehicle], visited_points: Set[Point]):
        max_attempts = 50
        attempts = 0

        while any(demand > 0 for demand in point.remaining_demand.values()) and attempts < max_attempts:
            attempts += 1
            best_vehicle = self._find_best_available_vehicle(vehicles, point)

            if best_vehicle is None:
                self._reload_all_empty_vehicles(vehicles)
                best_vehicle = self._find_best_available_vehicle(vehicles, point)

            if best_vehicle is None:
                raise RuntimeError(f"No vehicle can serve point {point.id}")

            delivery = self._calculate_possible_delivery(best_vehicle, point)

            if not delivery or all(qty <= 0 for qty in delivery.values()):
                if sum(best_vehicle.current_load.values()) == 0:
                    best_vehicle.add_stop(self.warehouse, is_warehouse=True)
                    best_vehicle.reload()
                    continue
                else:
                    raise RuntimeError(f"Vehicle {best_vehicle.id} has load but can't deliver to point {point.id}")

            best_vehicle.add_stop(point, delivery)
            for product, qty in delivery.items():
                point.remaining_demand[product] -= qty
                best_vehicle.current_load[product] -= qty

        if attempts >= max_attempts:
            raise RuntimeError(f"Too many attempts to serve point {point.id}")

    def _find_best_available_vehicle(self, vehicles: List[Vehicle], point: Point) -> Vehicle:
        best_vehicle = None
        best_score = -1

        for vehicle in vehicles:
            delivery = self._calculate_possible_delivery(vehicle, point)

            if not delivery or all(qty <= 0 for qty in delivery.values()):
                continue

            current_pos = self._get_vehicle_current_position(vehicle)
            distance_to_point = current_pos.distance_to(point)
            total_delivery = sum(delivery.values())
            score = total_delivery / (distance_to_point + 1.0)

            if score > best_score:
                best_score = score
                best_vehicle = vehicle

        return best_vehicle

    def _calculate_possible_delivery(self, vehicle: Vehicle, point: Point) -> Dict[str, int]:
        delivery = {}
        for product, demand in point.remaining_demand.items():
            if isinstance(demand, dict):
                continue
            available = vehicle.current_load.get(product, 0)
            if isinstance(available, dict):
                continue
            if demand > 0:
                deliver_qty = min(demand, available)
                if deliver_qty > 0:
                    delivery[product] = deliver_qty
        return delivery

    def _get_vehicle_current_position(self, vehicle: Vehicle) -> Point:
        if not vehicle.route:
            return self.warehouse
        return vehicle.route[-1]["point"]

    def _reload_all_empty_vehicles(self, vehicles: List[Vehicle]):
        for vehicle in vehicles:
            if sum(vehicle.current_load.values()) == 0:
                current_pos = self._get_vehicle_current_position(vehicle)
                if current_pos != self.warehouse:
                    vehicle.add_stop(self.warehouse, is_warehouse=True)
                vehicle.reload()

    def _calculate_vehicle_distance(self, vehicle: Vehicle):
        vehicle.total_distance = 0
        last_point = self.warehouse
        for stop in vehicle.route:
            current_point = stop["point"]
            vehicle.total_distance += last_point.distance_to(current_point)
            last_point = current_point

    def run(self) -> List[Vehicle]:
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
                    child = parent1.copy()

                child = self.mutate(child)
                new_population.append(child)

            population = new_population

            if gen % 10 == 0:
                best_fitness = self.fitness(population[0])
                print(f"Generation {gen}: Best fitness = {best_fitness}")

        best_individual = min(population, key=self.fitness)
        best_vehicles = self.create_delivery_plan(best_individual)
        return best_vehicles
