from analysis.sentiment import analyze_sentiment
import pandas as pd


def test_sentiment():
    mock_data = {"title": ["Good", "Bad"]}
    df_mocked = pd.DataFrame(
        mock_data,
    )

    df_sentiment = analyze_sentiment(df_mocked)
    assert df_sentiment["sentiment_label"].iloc[0] == "positive"
    assert df_sentiment["sentiment_label"].iloc[1] == "negative"
