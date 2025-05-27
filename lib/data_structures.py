import random


class Point:
    """
    Class representing a delivery point.

    Attributes:
    - x (int): x-coordinate of the point.
    - y (int): y-coordinate of the point.
    - total_demand (dict): total demand of the point by product.
    - remaining_demand (dict): remaining demand of the point by product.
    - label (str): label of the point.
    """

    def __init__(self, x: int, y: int, demand: dict = None, label: str = None) -> None:
        self.x = x
        self.y = y
        self.label = label
        if demand:
            self.total_demand = demand
        else:
            self.total_demand = self.generate_random_demand()
        self.remaining_demand = self.total_demand.copy()

    @staticmethod
    def generate_random_demand() -> dict:
        """Generates a random demand between 100 kg and 200 kg distributed across goods."""
        total = random.randint(100, 200)
        orange = random.randint(0, total)
        tuna = random.randint(0, total - orange)
        uranium = total - orange - tuna
        return {"orange": orange, "tuna": tuna, "uranium": uranium}

    def deliver(self, product: str, amount: int) -> int:
        """Delivers a certain amount of goods to the point."""
        if product in self.remaining_demand:
            self.remaining_demand[product] = max(0, self.remaining_demand[product] - amount)
        return self.remaining_demand.get(product, 0)

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
        self.capacity = self.VEHICLE_TYPES[vehicle_type]

        # Capacity per product
        self.capacity_dict = {"orange": self.capacity,
                              "tuna": self.capacity,
                              "uranium": self.capacity}

        self.current_load = self.capacity_dict.copy()
        self.driven_by_cat = False
        self.tuna_eaten_by_cat = 0
        self.total_distance = 0.0

    def reset(self) -> None:
        """Resets load and route of the vehicle."""
        self.current_load = self.capacity_dict.copy()
        self.route = []
        self.total_distance = 0.0

    def reload(self) -> dict:
        """Reloads the vehicle to full capacity using default capacity."""
        self.current_load = self.capacity_dict.copy()
        return self.current_load

    def reload_with_capacity(self, capacity_dict: dict) -> dict:
        """Reloads the vehicle to full capacity using specified capacity dictionary."""
        self.current_load = capacity_dict.copy()
        self.capacity_dict = capacity_dict.copy()
        return self.current_load

    def add_stop(self, point: Point, delivery_amounts: dict = None, is_warehouse: bool = False) -> None:
        """Adds a stop to the vehicle's route."""
        if delivery_amounts is None:
            delivery_amounts = {k: 0 for k in self.current_load}

        stop_info = {
            "point": point,
            "delivery": delivery_amounts.copy(),
            "remaining_load": self.current_load.copy(),
            "is_warehouse": is_warehouse,
        }

        if not is_warehouse:
            stop_info["remaining_demand"] = point.remaining_demand.copy()

        self.route.append(stop_info)

        if not is_warehouse:
            for product, amount in delivery_amounts.items():
                if amount > 0:
                    self.current_load[product] -= amount
                    point.deliver(product, amount)

        # If cat is driving and this isn't the first stop, cat eats tuna
        if self.driven_by_cat and len(self.route) > 1:
            prev_point = self.route[-2]["point"]
            distance = prev_point.distance_to(point)
            tuna_to_eat = min(self.current_load["tuna"], distance)
            self.current_load["tuna"] -= tuna_to_eat
            self.tuna_eaten_by_cat += tuna_to_eat

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

    def dispatch_vehicle(self, vehicle: Vehicle) -> None:
        """Resets the vehicle and sends it out on a new delivery route."""
        vehicle.reset()
        self.load_vehicle(vehicle)
        vehicle.add_stop(self.location, is_warehouse=True)

    def process_returned_goods(self, vehicle: Vehicle) -> None:
        """Handles goods returned by a vehicle to the warehouse."""
        returned_goods = vehicle.current_load.copy()
        self.receive_goods(returned_goods)
        for product in vehicle.current_load:
            vehicle.current_load[product] = 0


class GingerCat:
    """
    A fat, ginger cat that works at the company.
    Every day, the cat randomly chooses one vehicle to drive and eats tuna at a rate of 1kg/km.
    """

    def __init__(self, name="Garfield"):
        self.name = name
        self.selected_vehicle = None
        self.total_tuna_eaten = 0

    def select_random_vehicle(self, vehicles):
        """Randomly selects a vehicle to drive for the day."""
        if self.selected_vehicle:
            self.selected_vehicle.driven_by_cat = False
            self.total_tuna_eaten += self.selected_vehicle.tuna_eaten_by_cat

        self.selected_vehicle = random.choice(vehicles)
        self.selected_vehicle.driven_by_cat = True
        self.selected_vehicle.tuna_eaten_by_cat = 0
        return self.selected_vehicle

    def get_total_tuna_eaten(self):
        """Returns the total amount of tuna eaten by the cat."""
        current = 0
        if self.selected_vehicle:
            current = self.selected_vehicle.tuna_eaten_by_cat
        return self.total_tuna_eaten + current

    def __str__(self):
        return f"{self.name}, the company's fat ginger cat"


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
    warehouses = generate_warehouses_and_vehicles(5, 5)

    for warehouse in warehouses:
        print(f"Warehouse {warehouse.id} located at ({warehouse.location.x}, {warehouse.location.y})")
        for vehicle in warehouse.vehicles:
            assigned = vehicle.assigned_warehouse.id if vehicle.assigned_warehouse else None
            print(f"  Vehicle {vehicle.id} (Type: {vehicle.type}) assigned to Warehouse {assigned}")

    cat = GingerCat()
    print(cat)
    all_vehicles = [vehicle for warehouse in warehouses for vehicle in warehouse.vehicles]
    selected_vehicle = cat.select_random_vehicle(all_vehicles)
    print(f"{cat.name} is driving vehicle {selected_vehicle.id} today.")
