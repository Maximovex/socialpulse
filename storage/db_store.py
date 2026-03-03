from sqlalchemy import text
from storage.database import get_connection
import pandas as pd


def save_stories(df: pd.DataFrame) -> None:
    with get_connection() as conn:
        for _, row in df.iterrows():
            conn.execute(
                text("""
                INSERT INTO stories 
                    (id, title, score, author, url, time, kids_count, type, controversy_score,sentiment,sentiment_label)
                VALUES 
                    (:id, :title, :score, :author, :url, :time, :kids_count, :type, :controversy_score, :sentiment, :sentiment_label)
                ON CONFLICT (id) DO UPDATE SET
                    score = EXCLUDED.score,
                    kids_count = EXCLUDED.kids_count,
                    controversy_score = EXCLUDED.controversy_score,
                    sentiment = EXCLUDED.sentiment,
                    sentiment_label = EXCLUDED.sentiment_label
            """),
                {
                    "id": row["id"],
                    "title": row["title"],
                    "score": row["score"],
                    "author": row.get("by"),
                    "url": row.get("url"),
                    "time": row["time"],
                    "kids_count": row["kids_count"],
                    "type": row["type"],
                    "controversy_score": row["controversy_score"],
                    "sentiment": row["sentiment"],
                    "sentiment_label": row["sentiment_label"],
                },
            )
        conn.commit()
