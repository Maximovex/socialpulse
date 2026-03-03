import asyncio
from storage.cleaner import clean_stories
from collector.hn_client import top_ids, fetch_stories
from storage.store import save_to_csv, save_to_parquet
from storage.db_store import save_stories
import pandas as pd
from analysis.sentiment import analyze_sentiment


async def collect_stories():
    ids = top_ids(1000)
    stories = await fetch_stories(ids)
    save_to_csv(stories, "data/raw/stories.csv")
    save_to_parquet(stories, "data/processed/stories.parquet")
    print(f"Saved {len(stories)} stories")



def process_stories():
    pd.set_option("display.max_columns", None)
    df = pd.read_csv("data/raw/stories.csv")
    df_clean = clean_stories(df)
    df_clean = df_clean.where(pd.notna(df_clean), None)
    df_clean = analyze_sentiment(df_clean)
    print(df_clean.head(5))
    save_stories(df_clean)
    print("Saved to postgres")
    save_to_parquet(df_clean, "data/processed/stories_clean.parquet")
    print(f"Saved to parquet {len(df_clean)} stories")


if __name__ == "__main__":
    asyncio.run(collect_stories())
    process_stories()