from typing import Any

from pydantic import BaseModel, ConfigDict, field_validator
from datetime import datetime, date


class StoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    time: datetime
    title: str
    score: int
    author: str | None
    sentiment_label: str | None
    kids_count: int


class TrendResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    date: date
    avg_sentiment: float
    story_count: int

    # @field_validator("avg_sentiment")
    # def round_sentiment(cls, v):
    #     return round(v,4)


class TrendEngagementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    date: date
    avg_score: float
    avg_comment: float


class StatsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    total_stories: int
    avg_score: float
    avg_sentiment: float
    most_active_author: str | None
    top_story_title: str | None
    top_story_score: int | None


class RankingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    title: str
    score: int
    date: date
    daily_rank: int
