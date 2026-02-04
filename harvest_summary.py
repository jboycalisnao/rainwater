import pandas as pd

def compute_harvest(df,
                    roof_area,
                    classrooms,
                    runoff_coeff,
                    gutter_eff,
                    first_flush):
    df = df.copy()

    df["harvest_L"] = (
        (df["rain_mm"] - first_flush).clip(lower=0)
        * roof_area * classrooms
        * runoff_coeff * gutter_eff
    )

    # Also compute harvest per classroom roof (L)
    df["harvest_L_per_class"] = df["harvest_L"] / classrooms

    return df


def summarize_harvest(df):
    years = df["synthetic_year"].nunique()

    summary = {}

    summary["annual_L"] = df["harvest_L"].sum() / years

    # Per-classroom summaries
    summary["annual_L_per_class"] = df["harvest_L_per_class"].sum() / years

    monthly = (
        df.groupby("month")["harvest_L"].sum() / years
    )
    summary["monthly_L"] = monthly.to_dict()

    monthly_per_class = (
        df.groupby("month")["harvest_L_per_class"].sum() / years
    )
    summary["monthly_L_per_class"] = monthly_per_class.to_dict()

    df = df.copy()
    df["week"] = ((df["day_of_year"] - 1) // 7) + 1
    weekly = df.groupby("week")["harvest_L"].sum() / years
    summary["weekly_L"] = weekly.to_dict()

    weekly_per_class = df.groupby("week")["harvest_L_per_class"].sum() / years
    summary["weekly_L_per_class"] = weekly_per_class.to_dict()

    return summary
