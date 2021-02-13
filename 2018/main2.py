import sys

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

def get_length(current_location, ride):  # tuple, Ride
    p1 = current_location
    p2 = (ride.a, ride.b)
    p3 = (ride.x, ride.y)
    return (abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])) + (abs(p2[0] - p3[0]) + abs(p2[1] - p3[1]))

def get_ride_value_density(current_location, ride, bonus, time_to_go):

    length = get_length(current_location, ride)

    if time_to_go > length:
        bonus = 0
    elif time_to_go < length:
        return 0

    return (ride.ride_distance() + bonus) / length

def get_ride_value_density_with_wait(current_location, ride, bonus, time_to_go):
    if time_to_go < get_length(current_location, ride):
        return 0
    return (ride.ride_distance() + bonus) / time_to_go

def solve():
    r, c, F, b, T, rides = read_input(sys.argv[1])
    cars = [[0, 0, 0] for __ in range(F)]

    output = [[] for __ in range(F)]
    score = 0
    
    for t in range(T):
        if t % 10 == 0:
            print(f"{100 * t / T}%")
        for c_idx, car in enumerate(cars):
            if car[2] == 0:
                densities = [get_ride_value_density(car[:2], ride, b, T - t) for ride in rides]
                #densities_with_wait = [get_ride_value_density_with_wait(car[:2], ride, b, T - t) for ride in rides]
                max_density = 0
                max_wait_density = 0
                best_ride = None

                for i, d in enumerate(densities):
                    if d > max_density:
                        max_density = d
                        best_ride = i

                #for i, d in enumerate(densities_with_wait):
                #    if d > max_wait_density:
                #        max_wait_density = d

                #if max_wait_density > max_density:
                #    continue

                if best_ride == None:
                    break
                
                length = get_length(car[:2], rides[best_ride])
                score += max_density * length
                car[2] += length
                car[0] = rides[best_ride].x
                car[1] = rides[best_ride].y
                output[c_idx].append(rides[best_ride].idx)
                rides.pop(best_ride)
            else:
                car[2] -= 1
    print(int(score))
    with open(f"output_new.txt", "w") as fl:
        for v in output:
            fl.write(f"{len(v)} {' '.join(str(x) for x in v)}\n")

if __name__ == "__main__":  # score: 42032303; pos: 1045
    solve()