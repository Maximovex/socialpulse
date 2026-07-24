from sqlalchemy import text
from storage.database import get_connection
import pandas as pd
from analysis.predictor import get_embeddings

def save_stories(df: pd.DataFrame) -> None:
    with get_connection() as conn:
        for _, row in df.iterrows():
            conn.execute(
                text("""
                INSERT INTO stories 
                    (id, title, score, author, url, time, kids_count, type, 
                    controversy_score,sentiment,sentiment_label,
                    roberta_label,roberta_score)
                VALUES 
                    (:id, :title, :score, :author, :url, :time, :kids_count, 
                    :type, :controversy_score, :sentiment, :sentiment_label,
                    :roberta_label,:roberta_score)
                ON CONFLICT (id) DO UPDATE SET
                    score = EXCLUDED.score,
                    kids_count = EXCLUDED.kids_count,
                    controversy_score = EXCLUDED.controversy_score,
                    sentiment = EXCLUDED.sentiment,
                    sentiment_label = EXCLUDED.sentiment_label,
                    roberta_label = EXCLUDED.roberta_label,
                    roberta_score = EXCLUDED.roberta_score
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
                    "roberta_label": row["roberta_label"],
                    "roberta_score": row["roberta_score"]
                },
            )
        conn.commit()

def enrich_embeddings(batch_size: int = 32) -> int:
    """Add embeddings to stories that don't have them"""
    from analysis.predictor import get_embeddings

    with get_connection() as conn:
        result = conn.execute(text("""
            SELECT id, title FROM stories 
            WHERE embedding IS NULL
            LIMIT :batch_size
        """), {"batch_size": batch_size})
        rows = result.fetchall()

    if not rows:
        return 0

    ids = [r.id for r in rows]
    titles = [r.title for r in rows]
    embeddings = get_embeddings(titles)

    with get_connection() as conn:
        for id, embedding in zip(ids, embeddings):
            conn.execute(text("""
                UPDATE stories 
                SET embedding = :embedding
                WHERE id = :id
            """), {"embedding": embedding.tolist(), "id": id})
        conn.commit()

    return len(ids)
