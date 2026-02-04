def rainfall_intensity_stats(df):
    stats = {}
    wet = df[df["state"] == "W"]

    if wet.empty:
        raise ValueError("No wet days found in dataset.")

    for m in range(1, 13):
        data = wet[wet["month"] == m]["rainfall"]
        if not data.empty:
            stats[m] = {
                "mean": data.mean(),
                "std": data.std(),
                "p90": data.quantile(0.9),
            }
    return stats
