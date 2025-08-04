# STEP 1: Generate forecast data

import pandas as pd
import numpy as np

# 5-minute intervals for 1 day
time_range = pd.date_range("00:00", "23:55", freq="5min").time
n = len(time_range)

np.random.seed(0)
demand = np.random.normal(50, 5, n).round(2)
generation = (demand - np.random.normal(0, 4, n)).clip(min=0).round(2)

pd.DataFrame({"time": time_range, "demand_mw": demand}).to_csv("data/demand_forecast.csv", index=False)
pd.DataFrame({"time": time_range, "generation_mw": generation}).to_csv("data/generation_forecast.csv", index=False)


# STEP 2: ADMS Logic with ILP Optimization + Feedback Loop

import pandas as pd
from pulp import LpProblem, LpVariable, LpMinimize, lpSum, LpBinary, PulpSolverError

# Load forecast data
df_demand = pd.read_csv("data/demand_forecast.csv")
df_generation = pd.read_csv("data/generation_forecast.csv")
df = pd.merge(df_demand, df_generation, on="time")

# Define controllable loads
loads = [
    {"name": "EV_charger", "power": 5, "priority": 3},
    {"name": "AC_unit", "power": 3, "priority": 2},
    {"name": "Industrial_pump", "power": 7, "priority": 1}
]

load_names = [load['name'] for load in loads]
load_powers = {load['name']: load['power'] for load in loads}
load_costs = {load['name']: load['priority'] for load in loads}

status = {name: True for name in load_names}
restore_cooldown = {name: 0 for name in load_names}  # feedback timer to avoid flapping
log = []
buffer = 2
cooldown_period = 3  # 3 time steps (15 minutes)

for i, row in df.iterrows():
    time = row['time']
    demand = row['demand_mw']
    generation = row['generation_mw']
    imbalance = demand - generation
    action = []

    for name in restore_cooldown:
        if restore_cooldown[name] > 0:
            restore_cooldown[name] -= 1

    if imbalance > buffer:
        prob = LpProblem("ShedLoads", LpMinimize)
        x = {name: LpVariable(name, cat=LpBinary) for name in load_names if status[name]}
        prob += lpSum([load_costs[name] * x[name] for name in x]), "TotalCost"
        prob += lpSum([load_powers[name] * x[name] for name in x]) >= imbalance

        try:
            prob.solve()
            for name in x:
                if x[name].varValue == 1:
                    status[name] = False
                    restore_cooldown[name] = cooldown_period
                    action.append(f"shed {name}")
        except PulpSolverError:
            action.append("solver failed")

    elif generation - demand > buffer:
        for name in load_names:
            if not status[name] and restore_cooldown[name] == 0:
                status[name] = True
                action.append(f"restored {name}")

    log.append({
        "time": time,
        "demand": demand,
        "generation": generation,
        "action": "; ".join(action) if action else "none"
    })

log_df = pd.DataFrame(log)
log_df.to_csv("logs/adms_log.csv", index=False)

shed_count = log_df['action'].str.contains("shed").sum()
restore_count = log_df['action'].str.contains("restored").sum()
print(f"Total interventions: {shed_count + restore_count}")
print(f"Shed events: {shed_count}, Restores: {restore_count}")

