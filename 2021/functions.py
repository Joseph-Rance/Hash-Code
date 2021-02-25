from random import random as rand_float
import numpy as np
import matplotlib.pyplot as plt

def get_count(cars, roads, no_intersections):

    intersections = [{} for i in range(no_intersections)]

    for road in roads:
        intersections[road.end][road.name] = 0

    for car in cars:
        for road in car.route:
            intersection = road.end
            intersections[intersection][road.name] += 1

    return intersections  # [{road name: number}, {road name: number}]

def shitty_simulate(roads, cars, lights, bonus, cars_at_intersection, penalisation_weight=0):
    
    '''
    ~~ A SHITTY BUT SPEEDY SIMULATION ~~
    intersection wait time = time with green light / number of cars (precompute)
    car times = sum of intersection wait times
    car reaches end after car time
    then divide total score by sum of the lights list to penalise massive ratios to power of 1 / penalisation
    '''

    est_wait_times = {}
    for road in roads:

        time = 0
        total_time = 0
        for i in lights[road.end]:
            total_time += i[1]
            if i[0] == road.name:
                time = i[1]

        try:
            est_wait_time_frac = (time / total_time) / cars_at_intersection[road.end][road.name]
        except ZeroDivisionError:
            est_wait_time_frac = time
        est_wait_times[road.name] = est_wait_time_frac

    score = 0

    for car in cars:
        time = 0
        for road in car.route:
            time += est_wait_times[road.name]
        score += bonus + (total_time - time)

    total_ratio_sum = sum([sum([i[1] for i in j]) for j in lights])
    return score * (total_ratio_sum)**(-penalisation_weight)

def evolve(roads, cars, counts, bonus, epochs, starting_vals, mutation_chance=0.001, pop_size=20, std=5, temp=15, delete_frac=0.5):
    solutions = []
    for __ in range(pop_size):
        solution = {}
        solution["vals"] = starting_vals
        solution["score"] = 0
        solution["delete_prob"] = 0
        solutions.append(solution)

    score_curve = []

    for __ in range(epochs):
        
        # delete 50% according to randomised scores

        # for i in range (50%)
            # copy a random solution
            # randomly change solution
            # add into list of solutions

        # get scores

        sum_scores = 0
        for s in solutions:
            score = shitty_simulate(roads, cars, s["vals"], bonus, counts)
            s["score"] = score
            sum_scores += score
        score_curve.append(sum_scores)
        
        for s in solutions:
            s["delete_prob"] = np.random.normal(s["score"], temp)

        sorted_solutions = sorted(solutions, key=lambda s : s["delete_prob"])  # delete probability is actaully the random score
        solutions = sorted_solutions[int(delete_frac * len(sorted_solutions)):]

        for s in solutions.copy():
            s_copy = s.copy()
            for schedule in s_copy["vals"]:
                for idx in range(len(schedule)):
                    if rand_float() < mutation_chance:
                        if rand_float() > 0.5:
                            schedule[idx] = (schedule[idx][0], schedule[idx][1] + np.random.normal(0, std))
                        else:
                            schedule[idx] = (schedule[idx][0], schedule[idx][1] - np.random.normal(0, std))

                        schedule[idx] = (schedule[idx][0], max(int(schedule[idx][1]), 0))

            solutions.append(s_copy)

    for s in solutions:
        score = shitty_simulate(roads, cars, s["vals"], bonus, counts)
        s["score"] = score
    
    best_score = 0
    best_solution = None

    for s in solutions:
        if s["score"] > best_score:
            best_score = s["score"]
            best_solution = s

    for schedule in best_solution["vals"]:
        schedule = sorted(schedule, key=lambda s : s[1], reverse=True)

    plt.plot(score_curve)
    plt.show()
    
    return best_solution["vals"], best_score