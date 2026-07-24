from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pandas as pd
from transformers import pipeline

vader = SentimentIntensityAnalyzer()
roberta = pipeline(
    "sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment-latest"
)


def analyze_sentiment(df: pd.DataFrame) -> pd.DataFrame:
    # VADER
    df["sentiment"] = df["title"].apply(
        lambda x: vader.polarity_scores(str(x))["compound"]
    )
    df["sentiment_label"] = df["sentiment"].apply(
        lambda x: "positive" if x >= 0.05 else "negative" if x <= -0.05 else "neutral"
    )

    # RoBERTa
    results = roberta(df["title"].tolist(), truncation=True, max_length=512)
    df["roberta_label"] = [r["label"] for r in results]
    df["roberta_score"] = [r["score"] for r in results]
    return df
