import pandas as pd

def build_reliability_table(
    df,
    tank_sizes,
    daily_demand_L
):
    if df.empty:
        raise ValueError("No harvest data available.")

    results = []

    inflow = df["harvest_L"].values
    n = len(inflow)

    for tank in tank_sizes:
        storage = tank
        shortage = 0

        for daily_in in inflow:
            storage = min(tank, storage + daily_in)

            if storage >= daily_demand_L:
                storage -= daily_demand_L
            else:
                shortage += 1
                storage = 0

        reliability = 100 * (1 - shortage / n)

        results.append({
            "tank_L": tank,
            "reliability_pct": round(reliability, 2)
        })

    return pd.DataFrame(results)
