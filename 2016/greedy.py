# order in terms of how many items are needed to succeed
# take each drone and assign it to the smallest unassigned task
# move the drones through the places to do the task (use or tools here)
# when a drone is finished, set it to the next task (weight by dist to task)

from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import numpy as np
from math import ceil
from copy import deepcopy

class Drone:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.inventory = {}

class Warehouse:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.inventory = {}

class Order:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.num_items = 0
        self.products = {} # key is product num, item is number of this product ordered
        
def read_input(filename):
    drones = []
    warehouses = []
    orders = []
    weights = []
    with open(filename, "r") as f:
        lines = f.read().splitlines()

        # Read first few lines
        rows, cols, num_drones, deadline, max_load = [int(x) for x in lines[0].split(" ")]
        weights = [int(x) for x in lines[2].split(" ")]
        num_warehouses = int(lines[3])
        curr = 4

        # Parse the warehouses
        for __ in range(num_warehouses):
            w_x, w_y = [int(x) for x in lines[curr].split(" ")]
            warehouse_inv = [int(x) for x in lines[curr + 1].split(" ")]
            new_warehouse = Warehouse(w_x, w_y)
            for (i, c) in enumerate(warehouse_inv):
                if c != 0:
                    new_warehouse.inventory[i] = c
            warehouses.append(new_warehouse)
            curr += 2

        # Set the initial position of each drone to the position of the first warehouse
        for __ in range(num_drones):
            drones.append(Drone(warehouses[0].x, warehouses[0].y))


        num_orders = int(lines[curr])
        curr += 1

        # Parse the orders
        for __ in range(num_orders):
            o_x, o_y = [int(x) for x in lines[curr].split(" ")]
            o_n = int(lines[curr + 1])
            o_inv = [int(x) for x in lines[curr + 2].split(" ")]
            new_order = Order(o_x, o_y)
            new_order.num_items = o_n
            for i in o_inv:
                if i in new_order.products:
                    new_order.products[i] += 1
                else:
                    new_order.products[i] = 1
            orders.append(new_order)
            curr += 3

    return rows, cols, deadline, max_load, drones, warehouses, orders, weights

def get_warehouse_from_location(x, y, warehouses):
    warehouse_index = -1
    for (i, w) in enumerate(warehouses):
        if w.x == x and w.y == y:
            # This is a warehouse
            warehouse_index = i
            break
    return warehouse_index

def update_warehouse_inventories(warehouses, instructions):
    new_warehouses = deepcopy(warehouses)
    for instr in instructions:  # ((x,y), [1,2,3,4,4,4,5,6,7,8])
        instr_x = instr[0][0]
        instr_y = instr[0][1]
        warehouse_index = get_warehouse_from_location(instr_x, instr_y, new_warehouses)
        if warehouse_index >= 0:
            warehouse = new_warehouses[warehouse_index]
            instr_products = instr[1]
            for p in instr_products:
                warehouse.inventory[p] -= 1
    return new_warehouses

def get_path(drone, warehouses, order, weights, max_drone_cap):  # make sure to do a deepcopy on warehouses

    def tsp(dist_matrix):
        
        def distance_callback(from_index, to_index):
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return dist_matrix[from_node][to_node]
            
        manager = pywrapcp.RoutingIndexManager(len(dist_matrix), 1, 0)
        routing = pywrapcp.RoutingModel(manager)
        transit_callback_index = routing.RegisterTransitCallback(distance_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
        solution = routing.SolveWithParameters(search_parameters)
        
        index = routing.Start(0)
        visited = []
        while not routing.IsEnd(index):
            visited.append(manager.IndexToNode(index))
            index = solution.Value(routing.NextVar(index))
        
        return visited[1:], solution.ObjectiveValue()  # does not return depot

    def dist(p1, p2):
        return ceil(((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)**0.5)
        
    def common_elements(list1, list2):
        result = []
        for element in list1:
            if element in list2:
                result.append(element)
                list2.remove(element)
        return result

    def create_dist_matrix(locations):
        matrix = np.zeros((len(locations), len(locations))).tolist()
        for l1 in range(len(matrix)):
            for l2 in range(len(matrix)):
                matrix[l1][l2] = dist(locations[l1], locations[l2])
        return matrix

    items = order.products
    items = {key:(val, weights[key]) for key, val in items.items()}

    if sum([i[1] for __, i in items.items()]) <= max_drone_cap:

        locations = []

        products_to_get = []
        for i, j in items.items():
            products_to_get += [i]*j[0]

        idx = 0
        while products_to_get != []:

            products_have = []
            for i, j in warehouses[idx].inventory.items():
                products_have += [i]*j

            common = common_elements(products_to_get.copy(), products_have)

            for i in common:
                products_to_get.remove(i)

            locations.append(((warehouses[idx].x, warehouses[idx].y), common))

            idx += 1

        dist_matrix = create_dist_matrix([(order.x, order.y)]+[i[0] for i in locations])
                
        order_visited, time = tsp(dist_matrix)

        products_to_get = []
        for i, j in items.items():
            products_to_get += [i]*j[0]

        instructions = []
        for i in order_visited:
            instructions.append((*locations[i-1],))
        instructions.append(((order.x, order.y), products_to_get))

        time -= dist(instructions[0][0], (order.x, order.y))
        time += dist(instructions[0][0], (drone.x, drone.y))

        drone.x, drone.y = order.x, order.y

        return time, instructions, drone  # instructions[0] = ((x, y), [objects picked or dropped])

    else:
        groups = []
        current = []
        current_weight = 0

        items = [(key, val) for key, val in order.products.items()]

        while items != []:
            next_weight = weights[items[0][0]]
            if current_weight + next_weight > max_drone_cap:
                groups.append(current)
                current, current_weight = [], 0
            current_weight += next_weight
            current.append(items.pop(0))

        main_instructions = []
        total_time = 0
        for group in groups:
            
            order = Order(order.x, order.y)
            order.num_items = sum(i[1] for i in group)
            order.products = {i:j for i, j  in group}
            time, instructions, drone = get_path(drone, warehouses, order, weights, max_drone_cap)
            total_time += time
            warehouses = update_warehouse_inventories(warehouses, instructions)
            main_instructions += instructions
            
        return total_time, main_instructions, drone

def solve():
    filename = "busy_day.in"
    __, __, deadline, max_load, drones, warehouses, orders, weights = read_input(filename)
    
    # Sort orders by number of items
    sorted_unassigned_orders = sorted(orders, key=lambda o: o.num_items)

    drone_availability = [0] * len(drones)

    timestep = num_instructions = 0
    instructions_str = ""
    order_counter = 0
    while timestep < deadline:
        # Assign each available drone the next smallest order
        for (i, d) in enumerate(drone_availability):
            if d == 0:
                # Found an available drone
                drone_order = sorted_unassigned_orders.pop(0)
                time, instructions, drones[i] = get_path(drones[i], deepcopy(warehouses), drone_order, weights, max_load)
                drone_availability[i] = time
                
                update_warehouse_inventories(warehouses, instructions)
                for n in instructions:
                    instr_warehouse = get_warehouse_from_location(n[0][0], n[0][1], warehouses)  # ((x, y), [objects picked or dropped])
                    instr_char = "L" if instr_warehouse >= 0 else "D"
                    prod_counts = {}
                    for p in n[1]:
                        if p in prod_counts:
                            prod_counts[p] += 1
                        else:
                            prod_counts[p] = 1
                    for p in prod_counts:
                        instructions_str += f"{i} {instr_char} {order_counter} {p} {prod_counts[p]}\n"
                        num_instructions += 1

                order_counter += 1

        drone_availability[i] -= 1
        timestep += 1
    
    with open("output.txt", "w") as f:
        f.write(f"{num_instructions}\n")
        f.write(instructions_str)

solve()