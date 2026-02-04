def extract_spells(df):
    spells = []
    current = df.loc[0, "state"]
    length = 1
    month = df.loc[0, "month"]

    for i in range(1, len(df)):
        if df.loc[i, "state"] == current:
            length += 1
        else:
            spells.append({"state": current, "length": length, "month": month})
            current = df.loc[i, "state"]
            length = 1
            month = df.loc[i, "month"]

    spells.append({"state": current, "length": length, "month": month})
    return spells
