import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from config import DIRS
from scipy import stats
from scipy.stats import ttest_ind
from statsmodels.stats.power import TTestIndPower
import numpy as np

def load_df() -> pd.DataFrame:
    return pd.read_parquet(DIRS["processed"] / "stories_clean.parquet")


def required_data():
    analysis = TTestIndPower()
    required_n = analysis.solve_power(
        effect_size=0.2,  # small effect
        power=0.8,  # 80% chance of detecting it
        alpha=0.05,  # significance threshold
    )
    print(f"Required sample size per group: {required_n:.0f}")


def plotting_scores_comments():
    df = load_df()
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))

    # distribution of score
    sns.histplot(df["score"], ax=axes[0])
    axes[0].set_title("Score Distribution")

    # distribution of comments
    sns.histplot(df["kids_count"], ax=axes[1])
    axes[1].set_title("Comments Distribution")

    # relationship between score and comments
    sns.scatterplot(data=df, x="score", y="kids_count", ax=axes[2])
    axes[2].set_title("Score vs Comments")
    plt.savefig(DIRS["processed"] / "correlation.png")
    plt.show()


def correlation_comments_score():
    df = load_df()
    correlation = df["score"].corr(df["kids_count"])
    print(f"Correlation: {correlation:.2f}")

    top_posts = df.nlargest(5, "score")[["title", "score", "kids_count"]]
    print(top_posts.to_string())


def hypothesis_test():
    df = load_df()
    most_discussed = df.nlargest(5, "kids_count")[["title", "score", "kids_count"]]
    print(most_discussed.to_string())

    negative = df[df["roberta_label"] == "negative"]["score"]
    positive = df[df["roberta_label"] == "positive"]["score"]

    t_stat, p_value = stats.ttest_ind(negative, positive)
    pooled_std = np.sqrt((negative.std() ** 2 + positive.std() ** 2) / 2)
    cohens_d = (negative.mean() - positive.mean()) / pooled_std
    print(f"Cohen's d: {cohens_d:.3f}")
    print(f"t-statistic: {t_stat:.3f}")
    print(f"p-value: {p_value:.3f}")


def t_stats_p_value_explain():
    df = load_df()
    fig, ax = plt.subplots(figsize=(10, 5))

    for label, color in [
        ("positive", "green"),
        ("negative", "red"),
        ("neutral", "gray"),
    ]:
        subset = df[df["sentiment_label"] == label]["score"]
        sns.kdeplot(subset, ax=ax, label=f"{label} (n={len(subset)})", color=color)

    ax.axvline(
        df[df["sentiment_label"] == "negative"]["score"].mean(),
        color="red",
        linestyle="--",
        alpha=0.5,
    )
    ax.axvline(
        df[df["sentiment_label"] == "positive"]["score"].mean(),
        color="green",
        linestyle="--",
        alpha=0.5,
    )

    ax.set_title("Score Distribution by Sentiment")
    ax.legend()
    plt.savefig(DIRS["processed"] / "sentiment_distributions.png")
    plt.show()


if __name__ == "__main__":
    hypothesis_test()
