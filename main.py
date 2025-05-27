import random
from typing import List
from lib.data_structures import Point, Vehicle, GingerCat
from lib.solver import GeneticAlgorithmVRP
from lib.io import save_routes
from lib.plot import plot_routes

def generate_points(num_points: int, num_warehouses: int = 4) -> List[Point]:
    """Generate random points with warehouses and delivery locations."""
    points = []

    # Generate warehouses
    for i in range(num_warehouses):
        x = random.randint(0, 100)
        y = random.randint(0, 100)
        warehouse = Point(x, y)
        warehouse.label = f"Warehouse {i+1}"
        warehouse.is_warehouse = True
        warehouse.total_demand = {"orange": 0, "tuna": 0, "uranium": 0}
        warehouse.remaining_demand = warehouse.total_demand.copy()
        points.append(warehouse)

    # Generate delivery points
    for i in range(num_points - num_warehouses):
        x = random.randint(0, 100)
        y = random.randint(0, 100)
        point = Point(x, y)
        point.label = f"Point {i+1}"
        point.total_demand = {
            "orange": random.randint(10, 100),
            "tuna": random.randint(5, 50),
            "uranium": random.randint(1, 20)
        }
        point.remaining_demand = point.total_demand.copy()
        points.append(point)

    return points

def create_vehicles(vehicle_types: list) -> List[Vehicle]:
    """
    Create vehicles strictly according to counts defined in vehicle_types.
    """
    vehicles = []
    vehicle_id_counter = 1

    for vt in vehicle_types:
        for _ in range(vt["count"]):
            vehicle = Vehicle(vehicle_id_counter, vt['type'])
            vehicle.capacity = vt['capacity']
            vehicles.append(vehicle)
            vehicle_id_counter += 1

    return vehicles

def assign_cat_to_vehicle(vehicles: List[Vehicle], cat: GingerCat) -> None:
    """Randomly assign the cat to one of the vehicles and calculate tuna eaten."""
    active_vehicles = [v for v in vehicles if len(v.route) > 2]
    if active_vehicles:
        cat.select_random_vehicle(active_vehicles)
        selected_vehicle = cat.selected_vehicle

        total_tuna_delivered = 0
        for stop in selected_vehicle.route:
            if 'delivery' in stop and 'tuna' in stop['delivery']:
                total_tuna_delivered += stop['delivery']['tuna']

        tuna_eaten = total_tuna_delivered * 0.1

        selected_vehicle.driven_by_cat = True
        selected_vehicle.tuna_eaten_by_cat = tuna_eaten

        print(f"🐱 {cat.name} has chosen vehicle {selected_vehicle.id} for today's drive!")
        print(f"🐱 {cat.name} ate approximately {tuna_eaten:.2f}kg of tuna on this route.")
    else:
        print(f"🐱 {cat.name} couldn't find any active vehicles to drive today.")

def main():
    random.seed(230)

    print("🚚 Januszex Delivery Service - Route Optimization")
    print("=" * 50)

    num_points = 15
    points = generate_points(num_points, num_warehouses=1)

    print(f"Generated {len(points)} points:")
    for i, point in enumerate(points):
        if getattr(point, 'is_warehouse', False):
            print(f"  {i}: {point.label} (Warehouse)")
        else:
            demands = ", ".join(f"{k}:{v}" for k, v in point.total_demand.items())
            print(f"  {i}: {point.label} - Demands: {demands}")

    vehicle_types = [
        {"type": "green", "capacity": {"orange": 500, "tuna": 300, "uranium": 100}, "count": 2},
        {"type": "red", "capacity": {"orange": 800, "tuna": 500, "uranium": 200}, "count": 2},
    ]

    print(f"\nVehicle types:")
    for vt in vehicle_types:
        cap_str = ", ".join(f"{k}:{v}" for k, v in vt["capacity"].items())
        print(f"  {vt['type']}: {cap_str} (Count: {vt['count']})")

    company_cat = GingerCat("Mr. Whiskers")
    print(f"\n🐱 Company mascot: {company_cat.name}")

    print(f"\n🧬 Running Genetic Algorithm...")
    print(f"Population size: 50, Generations: 50")

    ga = GeneticAlgorithmVRP(
        points=points,
        vehicle_types=vehicle_types,
        population_size=50,
        generations=50
    )

    try:
        routes = ga.run()
        print(f"✅ Route optimization completed!")

        assign_cat_to_vehicle(routes, company_cat)

        print("\n📋 Generated delivery routes:")
        print("=" * 50)

        total_distance = 0
        active_vehicles = 0

        for vehicle in routes:
            if len(vehicle.route) <= 2:
                continue

            active_vehicles += 1
            total_distance += vehicle.total_distance

            print(f"\n🚛 Vehicle {vehicle.id} (Type: {vehicle.type}):")
            print(f"   Total distance: {vehicle.total_distance:.2f}")

            for i, stop in enumerate(vehicle.route):
                label = stop['point'].label
                line = f"   {i+1}. {label}"

                if 'delivery' in stop and any(v > 0 for v in stop['delivery'].values()):
                    delivered = ", ".join(f"{k}:{v}" for k, v in stop['delivery'].items() if v > 0)
                    line += f" - Delivered: {delivered}"
                elif getattr(stop['point'], 'is_warehouse', False):
                    line += " (Warehouse)"

                print(line)

            if getattr(vehicle, 'driven_by_cat', False):
                print(f"   🐱 {company_cat.name} drove this vehicle!")
                if hasattr(vehicle, 'tuna_eaten_by_cat'):
                    print(f"   🐟 Tuna consumed by cat: {vehicle.tuna_eaten_by_cat:.2f}kg")

        print(f"\n📊 Summary:")
        print(f"   Active vehicles: {active_vehicles}")
        print(f"   Total distance: {total_distance:.2f}")
        print(f"   Average distance per vehicle: {total_distance / max(1, active_vehicles):.2f}")

        save_routes(routes, "output/routes.txt")
        plot_routes(routes, points)

        print(f"\n💾 Routes saved to: output/routes.txt")
        print(f"📈 Route visualization saved")

    except Exception as e:
        print(f"❌ Error during route optimization: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
