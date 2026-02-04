def validate_model(hist_df, synth_df):
    return {
        "historical_mean_mm": hist_df["rainfall"].mean(),
        "synthetic_mean_mm": synth_df["rain_mm"].mean(),
        "historical_wet_pct": (hist_df["state"] == "W").mean() * 100,
        "synthetic_wet_pct": synth_df["wet"].mean() * 100,
    }
