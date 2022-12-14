from dataclasses import dataclass
from datetime import date, datetime

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

sns.set_theme()


@dataclass
class TimelineEvent:
    date: date
    name: str


def plot_reddit_data_over_time_subreddits(df: pd.DataFrame, column: str, label: str | None = None):
    subreddits = df["subreddit"].unique()

    data = {datetime.fromtimestamp(d).date(): {} for d in df["created_utc"]}
    for entry in df.iloc:
        key = datetime.fromtimestamp(entry["created_utc"]).date()
        subreddit = entry["subreddit"]
        data[key][subreddit] = data[key].get(subreddit, 0) + entry[column]

    for subreddit in subreddits:
        values = [v.get(subreddit, 0) for v in data.values()]
        sns.lineplot(x=data.keys(), y=values, label=f"r/{subreddit}")

    plt.legend()
    plt.ylabel(label or column)
    plt.xlabel("Date")
    plt.savefig(f"reddit_{column}_subreddits.pdf", dpi=400)
    plt.close()


def plot_reddit_data_over_time(df: pd.DataFrame, column: str, label: str | None = None):
    data = {datetime.fromtimestamp(d).date(): 0 for d in df["created_utc"]}
    for entry in df.iloc:
        key = datetime.fromtimestamp(entry["created_utc"]).date()
        data[key] += entry[column]

    sns.lineplot(x=data.keys(), y=data.values())

    plt.ylabel(label or column)
    plt.xlabel("Date")
    plt.savefig(f"reddit_{column}.pdf", dpi=400)
    plt.close()
