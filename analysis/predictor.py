import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
from xgboost import XGBRegressor
from config import DIRS




def prepare_features(df: pd.DataFrame) -> tuple:
    df = engineer_features(df)

    # encode categorical
    df["roberta_label_enc"] = df["roberta_label"].map(
        {"positive": 1, "neutral": 0, "negative": -1}
    )

    feature_cols = [
        "has_ask_hn", "has_show_hn", "has_question",
        "has_number", "word_count", "has_year",
        "hour", "day_of_week",
        "roberta_score", "roberta_label_enc", "sentiment"
    ]

    X = df[feature_cols].fillna(0)
    y = df["score"]

    return X, y


def train_model(df: pd.DataFrame):
    x, y = prepare_features(df)

    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.2, random_state=42
    )

    # Random Forest
    rf = RandomForestRegressor(n_estimators=100, random_state=42)
    rf.fit(x_train, y_train)
    rf_pred = rf.predict(x_test)

    # XGBoost
    xgb = XGBRegressor(n_estimators=100, random_state=42)
    xgb.fit(x_train, y_train)
    xgb_pred = xgb.predict(x_test)

    print("Random Forest:")
    print(f"  MAE: {mean_absolute_error(y_test, rf_pred):.1f}")
    print(f"  R²:  {r2_score(y_test, rf_pred):.3f}")

    print("XGBoost:")
    print(f"  MAE: {mean_absolute_error(y_test, xgb_pred):.1f}")
    print(f"  R²:  {r2_score(y_test, xgb_pred):.3f}")

    return rf, xgb, x_test, y_test

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    # Title features
    df["has_ask_hn"] = df["title"].str.startswith("Ask HN").astype(int)
    df["has_show_hn"] = df["title"].str.startswith("Show HN").astype(int)
    df["has_question"] = df["title"].str.endswith("?").astype(int)
    df["has_number"] = df["title"].str.contains(r'\d').astype(int)
    df["word_count"] = df["title"].str.split().str.len()
    df["has_year"] = df["title"].str.contains(r'\(20\d\d\)').astype(int)

    # Time features
    df["hour"] = pd.to_datetime(df["time"]).dt.hour
    df["day_of_week"] = pd.to_datetime(df["time"]).dt.dayofweek

    return df

def important_features_check(df: pd.DataFrame):
    import matplotlib.pyplot as plt

    feature_cols = [
        "has_ask_hn", "has_show_hn", "has_question",
        "has_number", "word_count", "has_year",
        "hour", "day_of_week",
        "roberta_score", "roberta_label_enc", "sentiment"
    ]

    rf, xgb, X_test, y_test = train_model(df)

    importance = pd.Series(rf.feature_importances_, index=feature_cols)
    importance.sort_values().plot(kind="barh", figsize=(10, 6))
    plt.title("Feature Importance - Random Forest")
    plt.tight_layout()
    plt.savefig(DIRS["processed"]/"feature_importance.png")
    plt.show()

_TOKENIZER = None
_MODEL = None


def _get_embedding_model():
    global _TOKENIZER, _MODEL
    if _TOKENIZER is None or _MODEL is None:
        from transformers import AutoTokenizer, AutoModel
        _TOKENIZER = AutoTokenizer.from_pretrained(
            "cardiffnlp/twitter-roberta-base-sentiment-latest"
        )
        _MODEL = AutoModel.from_pretrained(
            "cardiffnlp/twitter-roberta-base-sentiment-latest"
        )
    return _TOKENIZER, _MODEL

def get_embeddings(titles: list[str]) -> np.ndarray:
    import torch
    tokenizer, model = _get_embedding_model()
    embeddings = []
    for title in titles:
        inputs = tokenizer(
            title,
            return_tensors="pt",
            truncation=True,
            max_length=512
        )
        with torch.no_grad():
            outputs = model(**inputs)
        # use [CLS] token embedding as sentence representation
        embedding = outputs.last_hidden_state[0, 0].numpy()
        embeddings.append(embedding)
    return np.array(embeddings)


def train_with_embeddings(df: pd.DataFrame):
    print("Generating embeddings...")
    df=engineer_features(df)
    embeddings = get_embeddings(df["title"].tolist())

    # combine embeddings with time features
    time_features = df[["hour", "day_of_week"]].fillna(0).values
    X = np.hstack([embeddings, time_features])
    y = df["score"].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    rf = RandomForestRegressor(n_estimators=100, random_state=42)
    rf.fit(X_train, y_train)
    pred = rf.predict(X_test)

    print(f"Embeddings + RF:")
    print(f"  MAE: {mean_absolute_error(y_test, pred):.1f}")
    print(f"  R²:  {r2_score(y_test, pred):.3f}")


from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score


def train_classifier(df: pd.DataFrame):
    df = engineer_features(df)

    # create target
    threshold = df["score"].quantile(0.75)
    df["is_popular"] = (df["score"] > threshold).astype(int)

    print(f"Popular threshold: {threshold:.0f} points")
    print(f"Popular stories: {df['is_popular'].sum()} / {len(df)}")

    df["roberta_label_enc"] = df["roberta_label"].map(
        {"positive": 1, "neutral": 0, "negative": -1}
    )

    feature_cols = [
        "has_ask_hn", "has_show_hn", "has_question",
        "has_number", "word_count", "has_year",
        "hour", "day_of_week",
        "roberta_score", "roberta_label_enc", "sentiment"
    ]

    X = df[feature_cols].fillna(0)
    y = df["is_popular"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    rf = RandomForestClassifier(n_estimators=100, random_state=42,
                                class_weight="balanced")
    rf.fit(X_train, y_train)
    pred = rf.predict(X_test)

    print(classification_report(y_test, pred))
    print(f"ROC-AUC: {roc_auc_score(y_test, rf.predict_proba(X_test)[:, 1]):.3f}")

    return rf
