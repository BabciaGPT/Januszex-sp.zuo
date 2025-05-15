import random
from lib.data_structures import Point, Vehicle, GingerCat
from lib.solver import GeneticAlgorithmVRP
from lib.io import save_routes
from lib.plot import plot_routes
from random import randint

def generate_points(num_points: int, num_warehouses: int = 5) -> list:
    points = []

    # Creating warehouses
    for i in range(num_warehouses):
        x = random.randint(0, 100)
        y = random.randint(0, 100)
        points.append(Point(x, y, label=f"Warehouse {i+1}"))

    # Creating delivery points with random demand
    for _ in range(num_points - num_warehouses):
        x = random.randint(0, 100)
        y = random.randint(0, 100)
        label = f"Point ({x},{y})"
        points.append(Point(x, y, label=label))

    return points

def create_vehicles(num_vehicles: int) -> list:
    return [Vehicle.create_random_vehicle(vehicle_id=i) for i in range(num_vehicles)]


def main():
    random.seed(1)

    num_points = 30
    points = generate_points(num_points)

    num_vehicles = 5
    vehicles = create_vehicles(num_vehicles)
    
    company_cat = GingerCat("Mr. Whiskers")
    company_cat.select_random_vehicle(vehicles)
    print(f"🐱 {company_cat.name} has chosen vehicle {company_cat.selected_vehicle.id} for today's drive!")

    ga = GeneticAlgorithmVRP(points, num_vehicles)
    routes = ga.run()

    print("Generated delivery routes for vehicles:")
    for i, vehicle in enumerate(routes, 1):
        print(f"Vehicle {i} route:")
        for stop in vehicle.route:
            print(f"  - {stop['point'].label} (Demand: {stop['point'].remaining_demand})")
        
        if vehicle.driven_by_cat:
            print(f"  🐱 {company_cat.name} drove this vehicle and ate {vehicle.tuna_eaten_by_cat:.2f}kg of tuna!")

    save_routes(routes, "output/routes.txt")
    plot_routes(routes, points)


if __name__ == "__main__":
    main()

