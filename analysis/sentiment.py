from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pandas as pd

analyzer = SentimentIntensityAnalyzer()


def analyze_sentiment(df: pd.DataFrame) -> pd.DataFrame:
    df["sentiment"] = df["title"].apply(
        lambda x: analyzer.polarity_scores(str(x))["compound"]
    )
    df["sentiment_label"] = df["sentiment"].apply(
        lambda x: "positive" if x >= 0.05 else "negative" if x <= -0.05 else "neutral"
    )
    return df
