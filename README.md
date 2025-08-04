# Automatic Demand Management System (ADMS)  
### For Short-Term Load Forecasting (STLF) Project

---

## **Abstract**

This project builds an **Automatic Demand Management System (ADMS)** that uses short-term load forecasts to optimize how loads are shed or restored on a power grid. The system balances demand and generation every 5 minutes over a day using **Integer Linear Programming (ILP)**, prioritizing loads based on importance while avoiding rapid toggling with a feedback cooldown.

---

## **Introduction**

- The rise of renewable energy introduces variability in generation.
- Balancing real-time **demand and supply** is critical.
- **Short-Term Load Forecasting (STLF)** predicts demand and generation for near-future intervals.
- ADMS uses this forecast data to **shed or restore loads** smartly, ensuring grid stability and efficiency.

---

## **System Overview**

1. **Forecast Data Generation**
   - Simulates demand and renewable generation every 5 minutes for 24 hours.
   - Demand modeled as normal distribution (mean ~50 MW).
   - Generation derived by adjusting demand with noise to mimic renewables.

2. **Optimization-Based Load Management**
   - Controls three example loads:
     - **EV Charger** (5 MW, priority 3)
     - **AC Unit** (3 MW, priority 2)
     - **Industrial Pump** (7 MW, priority 1)
   - Uses ILP to minimize cost of shedding loads, ensuring shed power ≥ demand-generation imbalance.
   - Implements cooldown period to prevent rapid on/off switching.

---

## **Methodology**

- **Tools Used:**
  - Python 3.12
  - Libraries: `pandas`, `numpy`, `pulp` (with CBC solver)
  
- **Data Handling:**
  - Forecast CSVs saved in `/data/` directory.
  - ADMS action logs saved in `/log/` directory.
  
- **Optimization:**
  - Binary variables represent whether a load is shed (1) or not (0).
  - Objective: minimize total priority-weighted shedding cost.
  - Constraints ensure enough power is shed to cover imbalance.

- **Feedback Loop:**
  - Loads shed enter a cooldown for 15 minutes (3 timesteps).
  - Loads only restored if cooldown is over and generation surplus exists.

---

## **How to Run**

1. **Install required packages** if you haven’t already:

   ```bash
   pip install pandas numpy pulp


2. **Run the system script:**

   <pre> ```bash python3 AdmsSystem.py``` </pre>

---

## **Output**

- Forecast data saved to data/demand_forecast.csv and data/generation_forecast.csv.

- Load management logs saved to log/adms_log.csv.

- Terminal prints total number of load shedding and restoration interventions.

---

## Results


- The system performed 108 interventions in a 24-hour simulated day.

- 62 shedding events and 46 restoration events occurred.

- The ILP solver found optimal solutions quickly at each timestep.

- Demonstrates the feasibility of real-time load management using forecast-driven optimization.

## Future Improvements


- Use real-world forecast data instead of synthetic.

- Add more load types and support for multiple optimization objectives (e.g., cost, emissions).

- Incorporate uncertainty modeling and robust optimization.

- Build a dashboard to visualize demand, generation, and load actions live.

