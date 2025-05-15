def save_routes(vehicles: list, filename: str = "output/routes.txt") -> None:
    """Saves the delivery routes to a text file."""
    total_sum = 0.0
    with open(filename, "w") as f:
        for vehicle in vehicles:
            f.write(f"\nVehicle {vehicle.id} route:\n")
            
            if vehicle.driven_by_cat:
                f.write(f"🐱 This vehicle is driven by the company's fat ginger cat! 🐱\n")
            
            vehicle_distance = 0.0

            for i in range(len(vehicle.route) - 1):
                from_point = vehicle.route[i]["point"]
                to_point = vehicle.route[i + 1]["point"]
                vehicle_distance += from_point.distance_to(to_point)

            for stop in vehicle.route:
                point = stop["point"]
                if stop["is_warehouse"]:
                    f.write(
                        f"Warehouse | Load: {vehicle.capacity}/{vehicle.capacity}\n"
                    )
                else:
                    f.write(f"[Delivery] {point.label} | Total Demand: ")
                    for product, total in point.total_demand.items():
                        f.write(f"{product}: {total}kg, ")
                    f.write("| Delivered: ")
                    for product, amount in stop["delivery"].items():
                        f.write(f"{product}: {amount}kg, ")

                    f.write("| Remaining demand: ")
                    for product, rem in stop["remaining_demand"].items():
                        f.write(f"{product}: {rem}kg, ")

                    f.write("| Remaining load: ")
                    for product, load in stop["remaining_load"].items():
                        f.write(f"{product}: {load}kg, ")

                    f.write("\n")

            f.write(f"\nTotal distance: {vehicle_distance:.2f} km\n")
            
            if vehicle.driven_by_cat:
                f.write(f"Tuna eaten by the cat: {vehicle.tuna_eaten_by_cat:.2f} kg\n")
            
            total_sum += vehicle_distance

        f.write(f"\n\nGRAND TOTAL DISTANCE: {total_sum:.2f} km")
