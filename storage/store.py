import pandas as pd


def save_to_csv(stories: list[dict], path: str) -> None:
    df = pd.DataFrame(stories)
    df.to_csv(path, index=False)


def save_to_parquet(stories: list[dict], path: str) -> None:
    df = pd.DataFrame(stories)
    df.to_parquet(path, index=False)
