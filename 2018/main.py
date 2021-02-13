import sys
import vrp_function

class Ride:
    def __init__(self, idx, a, b, x, y, s, f):
        self.idx = idx
        self.a = a
        self.b = b
        self.x = x
        self.y = y
        self.s = s
        self.f = f
    
    def ride_distance(self):
        return abs(self.x - self.a) + abs(self.y - self.b)

def read_input(filename):
    rides = []

    with open(filename, "r") as fl:
        lines = fl.read().split("\n")
        index = 0
        r, c, F, n, b, t = [int(x) for x in lines[index].split(" ")]
        for __ in range(n):
            index += 1
            a, b, x, y, s, f = [int(x) for x in lines[index].split(" ")]
            ride = Ride(index - 1, a, b, x, y, s, f)
            rides.append(ride)
    
    return r, c, F, b, t, rides

def solve():
    filename = sys.argv[1]
    problem = filename[0]
    r, c, f, b, t, rides = read_input(filename)
    rides = sorted(rides, key=lambda r: r.ride_distance())
    solution_found, vehicle_rides, __ = vrp_function.VRP(rides, f, t)

    while not solution_found:
        print(len(rides))
        # Remove the shortest ride and try again ¯\_(ツ)_/¯
        rides = rides[1:]
        solution_found, vehicle_rides, __ = vrp_function.VRP(rides, f, t)

    # Solution found so now output it
    with open(f"output_{problem}.txt", "w") as fl:
        for v in vehicle_rides:
            fl.write(f"{len(v)} {' '.join(str(x) for x in v)}\n")

if __name__ == "__main__":
    solve()