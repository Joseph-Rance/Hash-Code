from ortools.linear_solver import pywraplp
import numpy as np
from time import time

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


# 1. capacities is rows split by crosses

# 2. matrix is servers as rows and capacities as columns
#   1 each element is an ohe with 1 in place of the group

# 3. Rules:
#   1 each row must have 0 or 1 1s
#   2 each column must sum to less than capacity

# 4. Maximise:
#   1 make array of sum of rows * value for each capacity * if row is deleted (1 or 0)
#   2 maximise min value in array

solver = pywraplp.Solver.CreateSolver("SCIP")

x = [[[0 for i in range(data["num_pools"])] for i in range(len(capacities))] for i in range(len(values))]
for i in range(len(x)):
    for j in range(len(x[0])):
        for k in range(len(x[0][0])):
            x[i][j][k] = solver.IntVar(0, 1, name=f"x_{i}_{j}_{k}")  # 1.1

for i in range(len(x)):
    solver.Add(sum(sum(x[i][j]) for j in range(len(capacities))) <= 1)  # 3.1

for j in range(len(x[0])):  # each column must sum to less than capacity
    solver.Add(sum(sum(x[i][j]) * weights[i] for i in range(len(x))) <= capacities[j])  # 3.2

# array y rows are row deleted
# array y cols are groups
# array y vals are scores

y = [[0 for i in range(data["num_pools"])] for i in range(len(capacities))]

for i in range(len(capacities)):
    for j in range(data["num_pools"]):
        y[i][j] = solver.IntVar(0, 10000, name=f"y_{i}_{j}")  # 1.1

print(np.asarray(x).shape)

for r in range(len(y)):
    for group in range(len(y[0])):  # can i do this?
        solver.Add(y[r][group] == sum([sum([x[server][row_sect][group] for row_sect in range(len(capacities)) if row_sect != r]) for server in range(len(x))]))
    print(r)
    print(time())

# answer = min of array y
answer = solver.IntVar(0, 1000, name="ans")
solver.Add(answer == min([min(i) for i in y]))  # can i do this?

print("SOLVING")

objective.SetCoefficient(answer, 1)
objective.SetMaximization()

status = solver.Solve()
if status == pywraplp.Solver.OPTIMAL:
    print(f"Total value: {objective.Value()}")
    for i in range(len(x)):
        for j in range(len(x[0])):
            print(np.argmax([x[i][j][k].solution_value() for k in range(len(x[0][0]))]), end=", ")
    with open("output.txt", "w") as f:
        f.write("\n".join([",".join([str(np.argmax([x[i][j][k].solution_value() for k in range(len(x[0][0]))])) for j in range(len(x[0]))]) for i in range(len(x))]))
else:
    print("NO")