from functions import *
from sys import argv

class Street:
    def __init__(self, start, end, name, time):
        self.start = start
        self.end = end
        self.name = name
        self.time = time

class Car:
    def __init__(self, route, start_intersection, start_street, start_position):
        self.route = route
        self.start_intersection = start_intersection
        self.start_street = start_street
        self.start_position = start_position
        self.timer = 0

def input_data(filename):
    with open(filename, "r") as f:
        streets = {}
        cars_end_of_streets = {}
        cars = []
        lines = f.read().split("\n")
        curr = 0
        d, I, s, v, f = [int(x) for x in lines[curr].split(" ")]
        for i in range(s):
            curr += 1
            start, end, name, time = lines[curr].split(" ")
            streets[name] = Street(int(start), int(end), name, int(time))
            cars_end_of_streets[name] = 1

        for i in range(v):
            curr += 1
            parts = lines[curr].split(" ")[1:]
            start_street = streets[parts[0]]
            route = []
            for p in parts:
                route.append(streets[p])
            cars.append(Car(route, start_street.end, start_street.name, cars_end_of_streets[start_street.name]))
            cars_end_of_streets[start_street.name] += 1
        
        return d, I, s, v, f, streets, cars

def solve():
    d, i, s, v, f, streets, cars = input_data(argv[1])
    counts = get_count(cars, streets.values(), i)
    lights = []
    for intersection in counts:
        schedule = []
        for street in intersection:
            schedule.append((street, intersection[street]))
        total = sum([i[1] for i in schedule])
        if total < 1:
            schedule[0] = (schedule[0][0], 1)
        lights.append(schedule)

    lights, score = evolve(streets.values(), cars, counts, f, 20, lights)
    print(score)

    for schedule in lights:
        total = sum([i[1] for i in schedule])
        if total < 1:
            schedule[0] = (schedule[0][0], 1)

    with open(f"output_{argv[1]}", "w") as f:
        f.write(f"{i}\n")
        for count, schedule in enumerate(lights):
            total = 0
            for __, time in schedule:
                if time > 0:
                    total += 1
            f.write(f"{count}\n{total}\n")
            for street, time in schedule:
                if time > 0:
                    f.write(f"{street} {time}\n")

if __name__ == "__main__":
    solve()