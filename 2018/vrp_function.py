from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from main import Ride

def get_length(r1, r2, rides):
    if r1 == r2:
        return 0

    r1, r2 = rides[r1], rides[r2]

    p1 = (r1.x, r1.y)  # end r1
    p2 = (r2.a, r2.b)  # start r2
    p3 = (r2.x, r2.y)  # end r2

    return (abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])) + (abs(p2[0] - p3[0]) + abs(p2[1] - p3[1]))

def VRP(rides, no_vehicles, finish_time):

    rides.insert(0, Ride(-1, 0, 0, 0, 0, 0, 5))

    time_matrix = [[0 for i in range(len(rides))] for i in range(len(rides))]

    for i in range(len(rides)):
        for j in range(len(rides)):
            time_matrix[i][j] = get_length(i, j, rides)

    times = []
    for ride in rides:
        times.append((ride.s, ride.f))

    depot = 0

    manager = pywrapcp.RoutingIndexManager(len(time_matrix), no_vehicles, depot)
    routing = pywrapcp.RoutingModel(manager)

    def time_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return time_matrix[from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(time_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    routing.AddDimension(transit_callback_index, int(finish_time/4), 2*finish_time, False, "Time")  # What do these mean?
    time_dimension = routing.GetDimensionOrDie("Time")
    
    for location_idx, time_window in enumerate(times):
        if location_idx == 0:
            continue
        index = manager.NodeToIndex(location_idx)
        time_dimension.CumulVar(index).SetRange(time_window[0], time_window[1])

    for vehicle_id in range(no_vehicles):
        index = routing.Start(vehicle_id)
        time_dimension.CumulVar(index).SetRange(times[0][0], times[0][1])

    for i in range(no_vehicles):
        routing.AddVariableMinimizedByFinalizer(time_dimension.CumulVar(routing.Start(i)))
        routing.AddVariableMinimizedByFinalizer(time_dimension.CumulVar(routing.End(i)))

    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

    print("SOLVING")

    solution = routing.SolveWithParameters(search_parameters)

    if not solution:
        return False, [], 0

    no_vehicles = no_vehicles

    vehicles_routes = [[] for i in range(no_vehicles)]

    time_dimension = routing.GetDimensionOrDie('Time')
    max_time = 0
    for vehicle_id, stops in enumerate(vehicles_routes):
        index = routing.Start(vehicle_id)
        while not routing.IsEnd(index):
            stops.append(manager.IndexToNode(index))
            index = solution.Value(routing.NextVar(index))
        max_time = max(max_time, solution.Min(time_dimension.CumulVar(index)))
        
    for i in range(len(vehicles_routes)):
        vehicles_routes[i] = vehicles_routes[i][1:]
        for j in range(len(vehicles_routes[i])):
            vehicles_routes[i][j] -= 1

    print(vehicles_routes, max_time)

    return True, vehicles_routes, max_time  # vehicles routes is shape (no. vehicles, no. stops for vehicle)