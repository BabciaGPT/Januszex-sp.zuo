import random
from lib.data_structures import Point, Vehicle
from lib.solver import GeneticAlgorithmVRP
from lib.io import save_routes
from lib.plot import plot_routes
from random import randint

def generate_points(num_points: int, num_warehouses: int = 5) -> list:
    points = []

    #Creating warehouses
    for i in range(num_warehouses):
        x = random.randint(0, 100)
        y = random.randint(0, 100)
        points.append(Point(x, y, label=f"Warehouse {i+1}"))

    #Creating points of delivery with different products
    for _ in range(num_points - num_warehouses):
        x = random.randint(0, 100)
        y = random.randint(0, 100)
        demand = {
            "orange": random.randint(50, 200),
            "uranium": random.randint(10, 50),
            "tuna": random.randint(30, 100),
        }
        label = f"Point ({x},{y})"
        points.append(Point(x, y, demand=demand, label=label))

    return points


def create_vehicles(num_vehicles: int) -> list:
    return [Vehicle.create_random_vehicle(vehicle_id=i) for i in range(num_vehicles)]


def main():
    random.seed(1)

    num_points = 30
    points = generate_points(num_points)

    num_vehicles = 5
    vehicles = create_vehicles(num_vehicles)

    ga = GeneticAlgorithmVRP(points, num_vehicles)
    routes = ga.run()

    print("Generated delivery routes for vehicles:")
    for i, vehicle in enumerate(routes, 1):
        print(f"Vehicle {i} route:")
        for stop in vehicle.route:
            print(f"  - {stop['point'].label} (Demand: {stop['point'].remaining_demand})")

    plot_routes(routes, points)


if __name__ == "__main__":
    main()
