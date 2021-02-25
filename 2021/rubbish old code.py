
# REMEMBER TO COPY IN CARS
def simulate(cars, roads, no_intersections, steps, lights, bonus):

    assert len(lights) == no_intersections
    
    '''
    cars is list of car objects
    roads is list of roads objects
    no_intersections is an integer
    steps is an integer
    lights is a list of intersection. Each intersection -> [(road, duration), (road, duration)]
    bonus is an integer
    '''

    score_a = 0
    score_b = 0

    intersections = [{} for i in range(no_intersections)]
    for road in roads:
        intersections[road.end][road.name] = []  # holds queue of cars at the intersection

    # add cars to intersections roads in correct order
    for car in cars:
        intersections[car.start_intersection][car.start_street].append(car)
    for i in range(len(intersections)):
        for j in intersections[i].keys():
            intersections[i][j] = sorted(intersections[i][j], key=lambda x : x.start_position)

    for car in cars:
        car.route.pop(0)
        if len(car.route) < 1:
            raise ValueError("AAAAAAAAAAAAAAAAAAAAAAAAAAAAA")

    for step in range(steps):

        for car in cars:
            car.timer -= 1

        for intersection, light in enumerate(lights):

            # get road with green light
            cycle_step = step % sum([i[1] for i in light])
            current = 0

            while cycle_step > 0:
                cycle_step -= light[current][1]
                current += 1
            if cycle_step < 0:
                current -= 1

            road = light[current][0]

            # remove first car from intersection of road and place on next intersection
            if len(intersections[intersection][road]) != 0:
                if intersections[intersection][road][0].timer <= 0:

                    car = intersections[intersection][road].pop(0)
                    
                    if car.route == []:
                        score_a += bonus
                        score_b += (steps - step)
                        del car
                    else:
                        intersections[car.route[0].end][car.route[0].name].append(car)
                        road = car.route.pop(0)  # remove street from route since we have covered it
                        car.timer = road.time

    print(score_a, score_b)

    return score_a + score_b