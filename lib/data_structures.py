import random


class Point:
    """
    Class representing a delivery point.

    Attributes:
    - x (int): x-coordinate of the point.
    - y (int): y-coordinate of the point.
    - total_demand (int): total demand of the point.
    - remaining_demand (int): remaining demand of the point.
    - label (str): label of the point
    """

    def __init__(self, x: int, y: int, demand: dict = None, label: str = None) -> None:
        self.x = x
        self.y = y
        self.label = label
        self.total_demand = demand if demand else {"orange": 0, "uranium": 0, "tuna": 0}
        self.remaining_demand = self.total_demand.copy()

    def deliver(self, product: str,amount: int) -> int:
        """Delivers a certain amount of goods to the point."""
        self.remaining_demand[product] = max(0, self.remaining_demand[product] - amount)
        return self.remaining_demand[product]

    def distance_to(self, other: "Point") -> float:
        """Calculates the Euclidean distance to another point."""
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5


class Vehicle:
    """
    Class representing a vehicle.
    """
    VEHICLE_TYPES = {
        "green": 1000,
        "blue": 1500,
        "red": 2000,
    }

    def __init__(self, vehicle_id: int, vehicle_type: str) -> None:
        if vehicle_type not in self.VEHICLE_TYPES:
            raise ValueError(f"Invalid vehicle type: {vehicle_type}")

        self.id = vehicle_id
        self.type = vehicle_type
        self.route = []
        self.assigned_warehouse = None
        self.current_load = {"orange": 0, "uranium": 0, "tuna": 0}
        self.capacity = {product: cap for product, cap in zip(self.current_load, [1000, 1500, 2000])}

    def reset(self) -> None:
        """Resets load and route of the vehicle."""
        self.current_load = self.capacity
        self.route = []

    def reload(self) -> dict:
        """Reloads the vehicle to full capacity."""
        self.current_load = self.capacity.copy()
        return self.current_load

    def add_stop(self, point: Point, delivery_amounts: dict = None, is_warehouse: bool = False) -> None:
        delivery_amounts = delivery_amounts or {k: 0 for k in self.current_load}

        if not is_warehouse:
            # Upewniamy się, że point ma strukturę demandu dla wszystkich towarów
            if not hasattr(point, "remaining_demand") or not isinstance(point.remaining_demand, dict):
                print(f"[WARNING] Point {getattr(point, 'label', 'UNKNOWN')} has no proper demand structure.")
                return
            for product in self.current_load:
                if product not in point.remaining_demand:
                    print(f"[WARNING] Point {getattr(point, 'label', 'UNKNOWN')} missing demand for '{product}'")
                    return

            # Sprawdzenie: nie wolno łączyć pomarańczy i uranu
            products = [product for product, amount in delivery_amounts.items() if amount > 0]
            if "orange" in products and "uranium" in products:
                print(
                    f"[INFO] Vehicle {self.id} skipped illegal combo (orange + uranium) at {getattr(point, 'label', 'UNKNOWN')}")
                return

        stop_info = {
            "point": point,
            "delivery": delivery_amounts.copy(),
            "remaining_load": self.current_load.copy(),
            "remaining_demand": point.remaining_demand.copy() if not is_warehouse else None,
            "is_warehouse": is_warehouse,
        }
        self.route.append(stop_info)

        if not is_warehouse:
            for product, amount in delivery_amounts.items():
                try:
                    deliverable = min(amount, point.remaining_demand[product], self.current_load[product])
                    self.current_load[product] -= deliverable
                    point.deliver(product, deliverable)
                except KeyError:
                    print(
                        f"[ERROR] Product '{product}' missing in either point or vehicle at {getattr(point, 'label', 'UNKNOWN')}")

    @staticmethod
    def create_random_vehicle(vehicle_id: int) -> "Vehicle":
        """Creates a vehicle with a random type."""
        vehicle_type = random.choice(list(Vehicle.VEHICLE_TYPES.keys()))
        return Vehicle(vehicle_id, vehicle_type)


class Warehouse:
    """
    Class representing a warehouse.

    Attributes:
    - id (int): Warehouse ID.
    - location (Point): The location of the warehouse.
    - vehicles (list): List of vehicles stationed at this warehouse.
    """

    def __init__(self, warehouse_id: int, location: Point, vehicles: list = None) -> None:
        self.id = warehouse_id
        self.location = location
        self.vehicles = vehicles if vehicles is not None else []

    def assign_initial_vehicle_positions(self, warehouses: list) -> None:
        """Randomly assigns each vehicle to a warehouse."""
        for vehicle in self.vehicles:
            vehicle.assigned_warehouse = random.choice(warehouses)

    def load_vehicle(self, vehicle: Vehicle) -> None:
        """Loads the vehicle to full capacity."""
        vehicle.reload()

    def receive_goods(self, amount: int) -> None:
        """Receives goods returned to the warehouse (unlimited storage)."""
        pass

    def dispatch_vehicle(self, vehicle: Vehicle) -> None:
        """Resets the vehicle and sends it out on a new delivery route."""
        vehicle.reset()
        self.load_vehicle(vehicle)
        vehicle.add_stop(self.location, is_warehouse=True)

    def process_returned_goods(self, vehicle: Vehicle) -> None:
        """Handles goods returned by a vehicle to the warehouse."""
        returned_goods = vehicle.current_load
        self.receive_goods(returned_goods)
        vehicle.current_load = 0



def generate_warehouses_and_vehicles(num_warehouses: int, num_vehicles_per_warehouse: int) -> list:
    warehouses = []
    for warehouse_id in range(num_warehouses):
        x = random.randint(0, 100)
        y = random.randint(0, 100)
        warehouse_location = Point(x, y, label=f"Warehouse {warehouse_id + 1}")

        vehicles = [Vehicle.create_random_vehicle(vehicle_id=i) for i in range(num_vehicles_per_warehouse)]

        warehouse = Warehouse(warehouse_id, warehouse_location, vehicles)
        warehouses.append(warehouse)

    for warehouse in warehouses:
        warehouse.assign_initial_vehicle_positions(warehouses)

    return warehouses


if __name__ == "__main__":
    warehouses = generate_warehouses_and_vehicles(5, 3)

    for warehouse in warehouses:
        print(f"Warehouse {warehouse.id} located at ({warehouse.location.x}, {warehouse.location.y})")
        for vehicle in warehouse.vehicles:
            print(f"  Vehicle {vehicle.id} (Type: {vehicle.type}) is assigned to this warehouse.")
