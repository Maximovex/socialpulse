from fastapi import FastAPI, HTTPException
from sqlalchemy import text
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.engine import row

from storage.database import get_connection
from api.schemas import StoryResponse, TrendResponse, StatsResponse, RankingResponse, TrendEngagementResponse

app = FastAPI(title="SocialPulse", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # in production, specify exact domains
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "SocialPulse API"}


@app.get("/stories", response_model=list[StoryResponse])
def get_stories(limit: int = 10, sentiment: str = None):
    with get_connection() as conn:
        if sentiment:
            result = conn.execute(
                text("""
                        SELECT id, time, title, score, author, sentiment_label, kids_count
                        FROM stories
                        WHERE sentiment_label = :sentiment
                        ORDER BY score DESC
                        LIMIT :limit
                    """),
                {"sentiment": sentiment, "limit": limit},
            )
        else:
            result = conn.execute(
                text("""
                        SELECT id, time, title, score, author, sentiment_label, kids_count
                        FROM stories
                        ORDER BY score DESC
                        LIMIT :limit
                    """),
                {"limit": limit},
            )

        return [dict(row._mapping) for row in result]

@app.get("/stories/{id}", response_model=StoryResponse)
def get_story(id: int):
    with get_connection() as conn:
        result = conn.execute(
            text("SELECT * FROM stories WHERE id = :id"),
            {"id": id}
        )
        row = result.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Story not found")
        return dict(row._mapping)

@app.get("/trends/sentiment",response_model=list[TrendResponse])
def get_trends(days: int = 7):
    with get_connection() as conn:
        result = conn.execute(
            text("""
                                   SELECT DATE(time) as date, ROUND(AVG(sentiment)::numeric,4) as avg_sentiment, COUNT(*) as story_count
                                   FROM stories
                                   GROUP BY DATE(time) ORDER BY date DESC
                                   LIMIT :days
                                   """),
            {"days": days},
        )
    return [dict(row._mapping) for row in result]

@app.get("/stats",response_model=StatsResponse)
def get_stats():
    with get_connection() as conn:
        result = conn.execute(
            text("""
                    WITH 
                    stats AS (
                        SELECT 
                            COUNT(*) as total_stories,
                            ROUND(AVG(score)::numeric, 2) as avg_score,
                            ROUND(AVG(sentiment)::numeric, 4) as avg_sentiment
                        FROM stories
                    ),
                    most_active_author AS (
                        SELECT author, COUNT(*) as post_count
                        FROM stories
                        GROUP BY author
                        ORDER BY post_count DESC
                        LIMIT 1
                    ),
                    top_story AS (
                        SELECT title, score
                        FROM stories
                        ORDER BY score DESC
                        LIMIT 1
                    )
                    SELECT 
                        s.total_stories,
                        s.avg_score,
                        s.avg_sentiment,
                        a.author as most_active_author,
                        t.title as top_story_title,
                        t.score as top_story_score
                    FROM stats s, most_active_author a, top_story t;
                """
        ),
            
        )
    row=result.fetchone()
    if row is None:
        return HTTPException(status_code=404, detail="No data available")
    return dict(row._mapping)

@app.get("/stories/rankings",response_model=list[RankingResponse])
def get_rankings(days: int = 7, top_n: int = 3):
    # return top N stories per day for the last X days
    with get_connection() as conn:
        result = conn.execute(
            text("""
            WITH ranked AS (
                SELECT title,score,DATE(time) as date, RANK() OVER (PARTITION BY DATE(time) 
                ORDER BY score DESC) as daily_rank
                FROM stories
                WHERE time >= NOW() - INTERVAL ':days days'
            )
            SELECT * FROM ranked WHERE daily_rank <= :top_n
            ORDER BY date DESC, daily_rank;
            """

            ),{"days": days,"top_n":top_n})
    return [dict(row._mapping) for row in result]

#populating database
@app.get("/collect")
async def collect_stories(limit:int=500):
    from collector.hn_client import top_ids, fetch_stories
    from storage.cleaner import clean_stories
    from storage.db_store import save_stories
    from analysis.sentiment import analyze_sentiment
    import pandas as pd

    ids = top_ids(limit)
    stories = await fetch_stories(ids)
    df = pd.DataFrame(stories)
    df = clean_stories(df)
    df = analyze_sentiment(df)
    save_stories(df)
    return {"collected": len(stories)}

#testing docker composing
@app.get("/health")
def health():
    return {"status": "ok", "version": "1.0"}

@app.get("/trends/engagement",response_model=list[TrendEngagementResponse])
def get_trends_engagement(days: int = 7):
    with get_connection() as conn:
        result = conn.execute(text("""
        SELECT ROUND(AVG(score)::numeric,2) as avg_score, ROUND(AVG(kids_count)::numeric,2) as avg_comment, DATE(time) as date  
        FROM stories GROUP BY date ORDER BY date DESC 
        """))
    return [dict(row._mapping) for row in result]

