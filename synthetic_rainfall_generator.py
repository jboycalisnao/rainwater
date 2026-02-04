import numpy as np
import pandas as pd

def generate_synthetic(spells, intensity, n_years=1, seed=2025):
    rng = np.random.default_rng(seed)
    records = []

    if not intensity:
        raise ValueError("Rainfall intensity parameters missing.")

    for y in range(n_years):
        day = 1
        while day <= 365:
            month = min(((day - 1) // 30) + 1, 12)
            wet = rng.random() < 0.4
            length = rng.integers(1, 6)

            for _ in range(length):
                if day > 365:
                    break
                rain = 0.0
                if wet and month in intensity:
                    mean = max(intensity[month]["mean"], 0.1)
                    rain = rng.gamma(shape=2.0, scale=mean / 2)

                records.append({
                    "synthetic_year": y + 1,
                    "day_of_year": day,
                    "month": month,
                    "rain_mm": rain,
                    "wet": int(wet)
                })
                day += 1

    return pd.DataFrame(records)
