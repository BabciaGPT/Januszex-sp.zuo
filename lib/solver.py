import random
from lib.data_structures import Point, Vehicle

class GeneticAlgorithmVRP:
    def __init__(self, points: list, num_vehicles: int):
        self.points = points
        self.num_vehicles = num_vehicles
        self.population_size = 100
        self.generations = 100
        self.mutation_rate = 0.1
        self.elite_size = 10

    def run(self):
        """Runs the genetic algorithm to generate the delivery routes."""
        population = self.create_initial_population()

        for generation in range(self.generations):
            population = self.evolve_population(population)

        best_routes = self.get_best_routes(population)
        return best_routes

    def create_initial_population(self):
        """Creates an initial population of routes."""
        population = []
        for _ in range(self.population_size):
            # Create a random route for each vehicle
            routes = self.create_random_routes()
            population.append(routes)
        return population

    def evolve_population(self, population):
        """Evolves the population using selection, crossover, and mutation."""
        new_population = []
        for _ in range(self.elite_size):
            new_population.append(self.select_parent(population))
        for _ in range(self.population_size - self.elite_size):
            parent1 = self.select_parent(population)
            parent2 = self.select_parent(population)
            child = self.crossover(parent1, parent2)
            new_population.append(self.mutate(child))
        return new_population

    def select_parent(self, population):
        """Selects a parent route based on fitness."""
        return random.choice(population)

    def crossover(self, parent1, parent2):
        """Performs crossover between two parents to create a child route."""
        return parent1

    def mutate(self, route):
        """Applies mutation to a route."""
        return route

    def get_best_routes(self, population):
        """Returns the best routes from the population."""
        return population[0]

    def create_random_routes(self):
        """Creates random routes for each vehicle."""
        routes = []
        for vehicle in range(self.num_vehicles):
            route = self.create_random_route_for_vehicle(vehicle)
            routes.append(route)
        return routes

    def create_random_route_for_vehicle(self, vehicle_id):
        """Creates a random route for a given vehicle."""
        random.shuffle(self.points)
        vehicle = Vehicle.create_random_vehicle(vehicle_id)
        vehicle.route = self.create_vehicle_route(vehicle)
        return vehicle

    def create_vehicle_route(self, vehicle):
        """Creates a route for a given vehicle."""
        route = []
        for point in self.points:
            if random.random() < 0.5:
                delivery = {
                    "orange": random.randint(0, point.remaining_demand["orange"]),
                    "uranium": random.randint(0, point.remaining_demand["uranium"]),
                    "tuna": random.randint(0, point.remaining_demand["tuna"]),
                }
                vehicle.add_stop(point, delivery_amounts=delivery)
                route.append({"point": point, "delivery": delivery})
        return route
