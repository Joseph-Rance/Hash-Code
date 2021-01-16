from ortools.linear_solver import pywraplp
import numpy as np
from time import time
from random import randint, seed

def pick_groups(servers, s, pools=45):
    seed(s)
    new_servers = []
    for server in servers:
        new_servers.append((*server, randint(0, pools-1)))
    return new_servers  # server is (index, row, section, group)

def get_score(servers_caps, servers_indexes, pools=45, rows=16):
    scores = [[0 for i in range(pools)] for i in range(rows)]

    # scores -> rows are deleted row; columns are groups

    for idx in range(len(servers_indexes)):
        for row in range(len(scores)):
            for col in range(len(scores[0])):
                if servers_indexes[idx][1] != row and servers_indexes[idx][3] == col:
                    scores[row][col] += servers_caps[idx].capacity

    return min([min(i) for i in scores])

class Server:
    def __init__(self, index, size, capacity):
        self.index = index
        self.size = size
        self.capacity = capacity

    def value(self):
        return self.capacity / self.size

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

data = read_data()
capacities = [[" "]*data["num_slots"] for i in range(data["num_rows"])]
for r, s in data["unavailable"]:
  capacities[r][s] = "X"
capacities = [("".join(i).split("X"),j) for j,i in enumerate(capacities)]
capacities = [(item, sublist[1]) for sublist in capacities for item in sublist[0]]
capacities = [(len(i),j) for i,j in capacities if len(i) != 0]  # capacities is (length, row idx)
rows = [i[1] for i in capacities]
capacities = [i[0] for i in capacities]  # changed my mind lmao

values = [i.capacity for i in data["servers"]]
weights = [i.size for i in data["servers"]]  # weight is width of server

solver = pywraplp.Solver.CreateSolver("SCIP")

x = [[0 for i in range(len(capacities))] for i in range(len(values))]
for i in range(len(weights)):
  for j in range(len(capacities)):
    x[i][j] = solver.IntVar(0, 1, name=f"x_{i}_{j}")  # create a binary variable for each element in array

for i in range(len(weights)):
  solver.Add(sum(x[i][j] for j in range(len(capacities))) <= 1)  # force each element to be in only 1 bin

for j in range(len(capacities)):
  solver.Add(sum(x[i][j] * weights[i] for i in range(len(weights))) <= capacities[j])  # force bin contents to be under capacity
objective = solver.Objective()
for i in range(len(weights)):
  for j in range(len(capacities)):
    objective.SetCoefficient(x[i][j], values[i])  # set value for each row to weight by
objective.SetMaximization()

status = solver.Solve()
if status == pywraplp.Solver.OPTIMAL:
    for j in range(len(capacities)):
        print(f"row: {rows[j]}, section: {j}")
        indexes = [i for i in range(len(values)) if x[i][j].solution_value()]
        print(indexes)
else:
    print("NO")

servers = []
for j in range(len(capacities)):
    servers += [(i, rows[j], j) for i in range(len(values)) if x[i][j].solution_value()]

print("setup done")

iterations = 10000
best_score = 0
best_choices = []
for i in range(iterations):
    new_servers = pick_groups(servers, i)
    score = get_score(data["servers"], new_servers)
    print(best_score)
    if score > best_score:
        best_choices = new_servers
        best_score = score

print(f"score: {best_score}")
