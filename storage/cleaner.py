import pandas as pd


def clean_stories(df: pd.DataFrame):
    df["kids_count"] = df["kids"].apply(
        lambda x: (
            len(str(x).split(","))
            if isinstance(x, (list, str)) and str(x) != "nan"
            else 0
        )
    )
    df = df.drop(columns=["kids", "text"])
    df["controversy_score"] = df["kids_count"] / (df["score"] + 1)
    df["time"] = pd.to_datetime(df["time"], unit="s")

    return df
