import pandas as pd

RAIN_ALIASES = [
    "rainfall", "rain", "rain_mm", "rr", "precip", "precipitation", "daily_rainfall"
]

DATE_ALIASES = [
    "date", "day", "datetime"
]

def load_and_clean(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    df.columns = [c.lower().strip() for c in df.columns]

    # Detect rainfall column
    rain_col = next((c for c in df.columns if c in RAIN_ALIASES), None)
    if rain_col is None:
        raise ValueError(f"No rainfall column found. Columns: {list(df.columns)}")
    # Always create a 'rainfall' column for downstream code
    if rain_col != "rainfall":
        df["rainfall"] = df[rain_col]

    # Detect date column
    date_col = next((c for c in df.columns if c in DATE_ALIASES or "date" in c), None)
    if date_col is None:
        raise ValueError("No date column found.")

    df["date"] = pd.to_datetime(df[date_col], errors="coerce")
    if df["date"].isna().any():
        raise ValueError("Invalid date values detected.")

    df["rainfall"] = pd.to_numeric(df["rainfall"], errors="coerce").fillna(0.0)
    df.loc[df["rainfall"] < 0, "rainfall"] = 0.0
    df["month"] = df["date"].dt.month

    return df[["date", "month", "rainfall"]].sort_values("date").reset_index(drop=True)
