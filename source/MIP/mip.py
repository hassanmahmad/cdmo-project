from z3 import *
import json
import sys
import time as time_module
from pathlib import Path
import math
from itertools import combinations
from pulp import *

def sports_tournament_schedule(n=6, timeout=300):
    
    # initialize variable from the data
    n = n % 2 == 0 and n or n + 1  # make n even
    week = n - 1
    period = math.ceil(n / 2)
    slots = 2
    total_games = week * period

    prob = LpProblem("STS", LpMinimize)

    schedule = [[[[LpVariable(f"s_{p}_{w}_{s}_{t}", cat="Binary") for t in range(n)] for s in range(slots)] for w in range(week)] for p in range(period)]
    
    # Adding Constraints
    for p in range(period):
        for w in range(week):
            # Each slot should have one team assigned to it
            for s in range(slots):
                prob += lpSum(schedule[p][w][s][t] for t in range(n)) == 1
            
            # no team plays against itself
            for t in range(n):
                prob += schedule[p][w][0][t] + schedule[p][w][1][t] <= 1

    # each team plays only once in a week
    for w in range(week):
        for t in range(n):
            prob += lpSum(schedule[p][w][s][t] for p in range(period) for s in range(slots)) == 1
    
    # each team play each other onlyonce in a tournament 
    # ESSENTIALLY CAN'T DO MULTIPLICATION in MIP WITH PuLP since it's not linear
    # for t1 in range(n):
    #     for t2 in range(t1 + 1, n):
    #         prob += lpSum(schedule[p][w][0][t1] * schedule[p][w][1][t2] + schedule[p][w][0][t2] * schedule[p][w][1][t1] for p in range(period) for w in range(week)) == 1

    # AGAIN, each team play each other onlyonce in a tournament 
    for t1 in range(n):
        for t2 in range(t1 + 1, n):
            matches_played = []
            for p in range(period):
                for w in range(week):
                    
                    # creating auxiliary variable to linearize the multiplication
                    m1 = LpVariable(f"m1_{p}_{w}_{t1}_{t2}", cat="Binary")
                    prob += m1 <= schedule[p][w][0][t1]
                    prob += m1 <= schedule[p][w][1][t2]
                    prob += m1 >= schedule[p][w][0][t1] + schedule[p][w][1][t2] - 1

                    m2 = LpVariable(f"m2_{p}_{w}_{t1}_{t2}", cat="Binary")
                    prob += m2 <= schedule[p][w][0][t2]
                    prob += m2 <= schedule[p][w][1][t1]
                    prob += m2 >= schedule[p][w][0][t2] + schedule[p][w][1][t1] - 1

                    matches_played.append(m1) 
                    matches_played.append(m2)

            # to constrain that they only play once
            prob += lpSum(matches_played) == 1
                    
        
    # no team play more than twice in the same period
    for t in range(n):
        for p in range(period):
            prob += lpSum(schedule[p][w][s][t] for w in range(week) for s in range(slots)) <= 2
    
    # balance the number of home and away games for each team
    for t in range(n):
        home_games = lpSum(schedule[p][w][0][t] for p in range(period) for w in range(week))
        away_games = lpSum(schedule[p][w][1][t] for p in range(period) for w in range(week))
        prob += home_games - away_games <= 1
        prob += away_games - home_games <= 1

    # reduce symmetries -- again by linearzing the multiplication
    for p in range(period):
        home_index = lpSum((t + 1) * schedule[p][0][0][t] for t in range(n))
        away_index = lpSum((t + 1) * schedule[p][0][1][t] for t in range(n))
        prob += home_index <= away_index - 1
    
    # solving the model
    start = time_module.time()
    prob.solve(PULP_CBC_CMD(timeLimit=timeout, msg=0))
    end = time_module.time() - start

    if prob.status == 1:  # Optimal
        
        sol = []
        for p in range(period):
            period_data = []
            for w in range(week):
                game = []
                for s in range(2):
                    for t in range(n):
                        if value(schedule[p][w][s][t]) > 0.5:
                            game.append(t + 1)
                            break
                period_data.append(game)
            sol.append(period_data)
        
        return {
            'time': int(end),
            'optimal': True,
            'obj': None,
            'sol': sol
        }
    
    else:
        return {
            'time': 300,
            'optimal': False,
            'obj': None,
            'sol': []
        }

if __name__ == '__main__':
    n = int(sys.argv[1])
    
    print(f"Solving with MIP for n={n}...")
    result = sports_tournament_schedule(n)
    
    # Save
    output_dir = Path('../../res/MIP')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(output_dir / f'{n}.json', 'w') as f:
        json.dump({'pulp_cbc': result}, f, indent=2)
    
    print(f"Done: Solution found: {result['optimal']}, Time: {result['time']}s")