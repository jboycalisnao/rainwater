def classify_wet_dry(df, threshold=0.1):
    df = df.copy()
    df["state"] = df["rainfall"].apply(lambda r: "W" if r >= threshold else "D")
    return df
