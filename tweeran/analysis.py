
from dataclasses import dataclass
from datetime import date, datetime

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.decomposition import PCA

from tweeran.extraction.reddit import RedditExtractionResult
from tweeran.nlp import get_bigrams, spacy_nlp

sns.set_theme()


def plot_entities_frequencies(data: pd.DataFrame, columns: list[str], exclude: str = "iran"):
    def extract_tokens(row) -> list[str]:
        tokens = []
        for c in columns:
            try:
                for ent in spacy_nlp(row[c]).ents:
                    if exclude in str(ent).lower():
                        continue
                    if ent.label_ in {'CARDINAL', 'ORDINAL', 'PERCENT', 'QUANTITY'}:
                        continue
                    tokens.append(ent.text)
            except ValueError:
                continue
        return tokens

    data["tokens"] = data.apply(extract_tokens, axis=1)  # type: ignore

    # groupby the values in the column, get the count and sort
    df_viz = data\
        .explode("tokens")\
        .groupby('tokens')["tokens"]\
        .count()\
        .reset_index(name='count')\
        .sort_values(['count'], ascending=False)\
        .head(10)\
        .reset_index(drop=True)

    sns.barplot(y=df_viz["tokens"], x=df_viz["count"])

    plt.ylabel("Entities")
    plt.xlabel("Frequencies")
    plt.savefig("reddit_frequencies.pdf", dpi=400, bbox_inches='tight')
    plt.close()


def plot_subreddits_submissions(data: RedditExtractionResult):
    sns.histplot(y=data.submissions["subreddit"])
    plt.savefig("reddit_subreddits_dist.pdf", dpi=400, bbox_inches='tight')
    plt.close()


def plot_users_subreddits(data: RedditExtractionResult, column: str = "author"):
    df_viz = data.submissions.groupby(by=['subreddit', column]).count()
    sns.barplot(y=df_viz["subreddit"], x=df_viz["count"])
    plt.ylabel("Entities")
    plt.xlabel("Frequencies")
    plt.savefig("reddit_users_subreddits.pdf", dpi=400, bbox_inches='tight')
    plt.close()


def plot_submissions_length(data: RedditExtractionResult):
    sns.displot(data.submissions, x="length")
    plt.xlim(0, 1000)
    plt.savefig("reddit_lengths_dist.pdf", dpi=400, bbox_inches='tight')
    plt.close()


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


def plot_bigrams(data: RedditExtractionResult):
    bigrams = []
    for row in data.submissions.iloc:
        if type(row["title"]) != str or type(row["selftext"]) != str:
            continue
        bigrams.extend(get_bigrams(" ".join([row["title"], row["selftext"]])))

    viz_data: dict[str, int] = {}
    embeddings = {}
    for bigram, vec in bigrams:
        viz_data[bigram] = viz_data.get(bigram, 0) + 1
        embeddings[bigram] = vec

    viz_df_base = []
    for bigram, count in viz_data.items():
        if bigram is None or type(bigram) != str:
            continue
        viz_df_base.append({"bigram": bigram, "count": count})

    viz_df = pd.DataFrame.from_records(viz_df_base)

    pca = PCA(n_components=2)
    pca_result = pca.fit_transform([vec for vec in embeddings.values()])

    viz_df["pca1"] = pca_result[:, 0]
    viz_df["pca2"] = pca_result[:, 1]

    viz_df.sort_values(by='count', ascending=False, inplace=True)

    sns.scatterplot(viz_df[:15], x="pca1", y="pca2", size="count")

    for i in range(15):
        plt.text(viz_df["pca1"][i], viz_df["pca2"][i], viz_df["bigram"][i],
                 horizontalalignment='left', size='small', color='black')

    plt.savefig("reddit_bigrams.pdf", dpi=400)
    plt.close()
