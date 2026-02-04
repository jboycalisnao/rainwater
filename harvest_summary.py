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

    return df


def summarize_harvest(df):
    years = df["synthetic_year"].nunique()

    summary = {}

    summary["annual_L"] = df["harvest_L"].sum() / years

    monthly = (
        df.groupby("month")["harvest_L"].sum() / years
    )
    summary["monthly_L"] = monthly.to_dict()

    df = df.copy()
    df["week"] = ((df["day_of_year"] - 1) // 7) + 1
    weekly = df.groupby("week")["harvest_L"].sum() / years
    summary["weekly_L"] = weekly.to_dict()

    return summary
