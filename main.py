import random
from typing import List
from lib.data_structures import Point, Vehicle, GingerCat
from lib.solver import GeneticAlgorithmVRP
from lib.io import save_routes
from lib.plot import plot_routes

def generate_points(num_points: int, num_warehouses: int = 4) -> List[Point]:
    """Generate random points with warehouses and delivery locations."""
    points = []

    for i in range(num_warehouses):
        x = random.randint(0, 100)
        y = random.randint(0, 100)
        warehouse = Point(x, y)
        warehouse.label = f"Warehouse {i+1}"
        warehouse.is_warehouse = True
        warehouse.total_demand = {"orange": 0, "tuna": 0, "uranium": 0}
        warehouse.remaining_demand = warehouse.total_demand.copy()
        points.append(warehouse)

    for i in range(num_points - num_warehouses):
        x = random.randint(0, 100)
        y = random.randint(0, 100)
        point = Point(x, y)
        point.label = f"Point {i+1}"
        points.append(point)

    return points

def create_vehicles(vehicle_types: list) -> List[Vehicle]:
    vehicles = []
    vehicle_id_counter = 1
    for vt in vehicle_types:
        for _ in range(vt['count']):
            vehicles.append(Vehicle(vehicle_id_counter, vt['type']))
            vehicle_id_counter += 1
    return vehicles

def assign_cat_to_vehicle(vehicles: List[Vehicle], cat: GingerCat) -> None:
    """Randomly assign the cat to one of the vehicles."""
    if vehicles:
        cat.select_random_vehicle(vehicles)
        print(f"🐱 {cat.name} has chosen vehicle {cat.selected_vehicle.id} for today's drive!")

def main():
    random.seed(1)

    num_points = 30
    points = generate_points(num_points)

    vehicle_types = [
        {"type": "green", "capacity": 1000, "count": 2},
        {"type": "red", "capacity": 2000, "count": 3},
    ]

    vehicles = create_vehicles(vehicle_types)

    company_cat = GingerCat("Mr. Whiskers")

    ga = GeneticAlgorithmVRP(
        points=points,
        vehicle_types=vehicle_types,
        population_size=50,
        generations=100
    )
    routes = ga.run()

    assign_cat_to_vehicle(routes, company_cat)

    print("\nGenerated delivery routes:")
    for vehicle in routes:
        print(f"\nVehicle {vehicle.id} (Type: {vehicle.type}, Capacity: {vehicle.capacity}):")
        for stop in vehicle.route:
            point_info = f"{stop['point'].label}"
            if 'delivery' in stop and any(v > 0 for v in stop['delivery'].values()):
                delivered = ", ".join(f"{k}:{v}" for k, v in stop['delivery'].items() if v > 0)
                point_info += f" - Delivered: {delivered}"
            print(f"  - {point_info}")

        if hasattr(vehicle, 'driven_by_cat') and vehicle.driven_by_cat:
            print(f"   {company_cat.name} drove this vehicle!")
            if hasattr(vehicle, 'tuna_eaten_by_cat'):
                print(f"  Tuna consumed: {vehicle.tuna_eaten_by_cat:.2f}kg")

    save_routes(routes, "output/routes.txt")
    plot_routes(routes, points)

if __name__ == "__main__":
    main()
