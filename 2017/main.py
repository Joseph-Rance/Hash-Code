import sys
from functions import knapsack, get_value, get_score
from random import shuffle, seed
from copy import deepcopy

class Cache:
    def __init__(self, cache_id):
        self.id = cache_id
        self.videos = []
        self.connected_endpoints = []

class Endpoint:
    def __init__(self, datacentre_latency, connected_caches):
        self.requests = {} # key is video id, value is num requests
        self.datacentre_latency = datacentre_latency
        self.connected_caches = connected_caches # key is cache server id, value is cache latency

def read_input(filename):
    with open(filename, "r") as f:
        # Stuff returned by this
        endpoints = []
        caches = []
        video_sizes = []

        lines = f.read().splitlines()
        curr = 0
        __, e, r, c, x = [int(n) for n in lines[curr].split(" ")]
        for i in range(c):
            caches.append(Cache(i))
        curr += 1
        video_sizes = [int(n) for n in lines[curr].split(" ")]
        curr += 1
        for i in range(e):
            ld, k = [int(n) for n in lines[curr].split(" ")]
            curr += 1
            connected_caches = {}
            for __ in range(k):
                c, lc = [int(n) for n in lines[curr].split(" ")]
                connected_caches[c] = lc
                caches[c].connected_endpoints.append(i)
                curr += 1
            endpoints.append(Endpoint(ld, connected_caches))
        for i in range(r):
            rv, re, rn = [int(n) for n in lines[curr].split(" ")]
            endpoints[re].requests[rv] = rn
            curr += 1
        return endpoints, caches, video_sizes, x

def solve(endpoints, caches, video_sizes, x):
    num_caches = len(caches)
    itr = 0
    for c in caches:
        print(f"\r{100 * itr / num_caches}%")
        values = [get_value(i, c, endpoints) for i in range(len(video_sizes))]
        __, items = knapsack(x, video_sizes, values)
        c.videos = items
        for e in c.connected_endpoints:
            endpoint = endpoints[e]
            for v in c.videos:
                if v in endpoint.requests:
                    endpoint.requests[v] = 0
        itr += 1
    return caches

def main():
    iterations = 10
    endpoints, caches, video_sizes, x = read_input(sys.argv[1])
    best_score, best_caches = 0, []
    for i in range(iterations):
        print(f"iteration: {i}")
        temp_caches = deepcopy(caches)
        temp_endpoints = deepcopy(endpoints)
        seed(i)
        shuffle(temp_caches)
        solve(temp_endpoints, temp_caches, video_sizes, x)
        score = get_score(temp_caches, endpoints)
        if score > best_score:
            best_score = score
            best_caches = temp_caches

    print(f"best score: {best_score}")

    with open("output.txt", "w") as f:
        f.write(str(len(best_caches)) + "\n")
        for cache in best_caches:
            f.write(" ".join([str(i) for i in cache.videos]) + "\n")

if __name__ == "__main__":  # time spent: 2hrs; score: 1858330; pos: 883/2815
    main()