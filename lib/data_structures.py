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

    def __init__(self, x: int, y: int, demand: int = 0, label: str = None) -> None:
        self.x = x
        self.y = y
        self.total_demand = demand
        self.remaining_demand = demand
        self.label = label

    def deliver(self, amount: int) -> int:
        """Delivers a certain amount of goods to the point."""
        self.remaining_demand = max(0, self.remaining_demand - amount)
        return self.remaining_demand

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
        self.capacity = self.VEHICLE_TYPES[vehicle_type]
        self.current_load = self.capacity
        self.route = []
        self.assigned_warehouse = None

    def reset(self) -> None:
        """Resets load and route of the vehicle."""
        self.current_load = self.capacity
        self.route = []

    def reload(self) -> int:
        """Reloads the vehicle to full capacity."""
        self.current_load = self.capacity
        return self.current_load

    def add_stop(self, point: Point, delivery_amount: int = 0, is_warehouse: bool = False) -> None:
        """Adds a stop to the vehicle's route."""
        stop_info = {
            "point": point,
            "delivery": delivery_amount,
            "remaining_load": self.current_load,
            "remaining_demand": point.remaining_demand if not is_warehouse else None,
            "is_warehouse": is_warehouse,
        }
        self.route.append(stop_info)

        if not is_warehouse:
            delivery_amount = min(delivery_amount, point.remaining_demand, self.current_load)
            self.current_load -= delivery_amount
            point.deliver(delivery_amount)

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
