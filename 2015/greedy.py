from random import random

# Represents a server
class Server:
    def __init__(self, index, size, capacity):
        self.index = index
        self.size = size
        self.capacity = capacity
        self.pool = None

    def value(self, t):
        return t * self.capacity + (1 - t) * self.capacity / self.size


# Reads all the data from the input file, returns a data dict
def read_data():
    data = {}
    with open("dc.in", "r") as f:
        lines = f.read().splitlines()

        curr_line = 0
        r, s, u, p, m = [int(x) for x in lines[0].split(" ")]
        curr_line += 1

        unavailable = []
        for i in range(u):
            u_line = lines[curr_line]
            ur, us = [int(x) for x in u_line.split(" ")]
            unavailable.append((ur, us))
            curr_line += 1

        servers = []
        for i in range(m):
            s_line = lines[curr_line]
            sz, sc = [int(x) for x in s_line.split(" ")]
            servers.append(Server(i, sz, sc))
            curr_line += 1

        data["num_rows"] = r
        data["num_slots"] = s
        data["unavailable"] = unavailable
        data["num_pools"] = p
        data["servers"] = servers

        return data

def solve():
    data = read_data()
    best_grid = []
    best_t = -1
    best_score = 0

    for _ in range(1):
        t = 0.18273103060237506
        sorted_servers = sorted(data["servers"], key=lambda s: s.value(t), reverse=True)
        
        # Grid containing servers
        grid = []
        for r in range(data["num_rows"]):
            grid.append([])
            for s in range(data["num_slots"]):
                grid[r].append(None)
        
        for u in data["unavailable"]:
            grid[u[0]][u[1]] = -1

        curr_pool = 0
        curr_row = 0

        # Used later for calculating score
        pool_capacities = [0 for _ in range(data["num_pools"])]

        for curr_server in sorted_servers:
            curr_server.pool = curr_pool

            # Find a place for the server, a bit like bin packing
            placed = False
            copy_curr_row = curr_row
            curr_slot = 0
            moved = False
            while not placed:
                # If we've run out of grid, we couldn't place the server
                if copy_curr_row == curr_row and moved:
                    break

                if grid[copy_curr_row][curr_slot] == None and curr_slot + curr_server.size - 1 < data["num_slots"]:
                    # Place server here
                    placed = True
                    pool_capacities[curr_pool] += curr_server.capacity
                    grid[copy_curr_row][curr_slot] = curr_server
                else:
                    # Don't place here, jump to next possible position
                    while grid[copy_curr_row][curr_slot] != None:
                        if grid[copy_curr_row][curr_slot] == -1:
                            curr_slot += 1
                        else:
                            # Jump over a server that has already been placed
                            jump_length = grid[copy_curr_row][curr_slot].size
                            curr_slot += jump_length
                        if curr_slot + curr_server.size - 1 >= data["num_slots"]:
                            curr_slot = 0
                            copy_curr_row = (copy_curr_row + 1) % data["num_rows"]
                            moved = True
                            break

            if placed:
                curr_pool = (curr_pool + 1) % data["num_pools"]
                curr_row = (curr_row + 1) % data["num_rows"]
        
        max_pool_losses = [0 for _ in range(data["num_pools"])]
        for r in range(data["num_rows"]):
            pool_losses = [0 for _ in range(data["num_pools"])]
            for s in range(data["num_slots"]):
                item = grid[r][s]
                if item != -1 and item != None:
                    # Item must be a server
                    pool_losses[item.pool] += item.capacity
            for l, loss in enumerate(pool_losses):
                max_pool_losses[l] = max(max_pool_losses[l], loss)
        
        for p in range(len(pool_capacities)):
            pool_capacities[p] -= max_pool_losses[p]
        
        score = min(pool_capacities)
        if score > best_score:
            best_grid = grid
            best_score = score
            best_t = t

    print(f"Best score: {best_score}")
    print(f"Best t value: {best_t}")

solve()