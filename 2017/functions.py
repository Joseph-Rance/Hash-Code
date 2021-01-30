from ortools.algorithms import pywrapknapsack_solver
from math import floor

def knapsack(capacity, sizes, values):

    sizes = [sizes]
    solver = pywrapknapsack_solver.KnapsackSolver(pywrapknapsack_solver.KnapsackSolver.KNAPSACK_MULTIDIMENSION_BRANCH_AND_BOUND_SOLVER, 'KnapsackExample')
    solver.Init(values, sizes, [capacity])
    computed_value = solver.Solve()

    items = []
    for i in range(len(values)):
        if solver.BestSolutionContains(i):
            items.append(i)

    return computed_value, items

def get_value(video_id, cache, endpoints):

    total = 0
    for endpoint in endpoints:
        if video_id in endpoint.requests and cache.id in endpoint.connected_caches:
            total += (endpoint.datacentre_latency - endpoint.connected_caches[cache.id]) * endpoint.requests[video_id]
    
    return total

def get_score(caches, endpoints):

    total = no_requests = 0
    for endpoint in endpoints:
        for video_id, number in endpoint.requests.items():
            no_requests += number
            best = endpoint.datacentre_latency
            for cache_id, latency in endpoint.connected_caches.items():
                if video_id in caches[cache_id].videos:
                    best = min(best, latency)
            total += (endpoint.datacentre_latency - best) * number
        
    return floor(total * 1000 / no_requests)