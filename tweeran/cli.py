
import argparse

import pandas as pd
import yaml

import tweeran


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="tweeran")
    parser.add_argument('-e', '--extract', type=bool,
                        action=argparse.BooleanOptionalAction,
                        default=False, required=False)
    parser.add_argument('-p', '--plot', type=bool,
                        action=argparse.BooleanOptionalAction,
                        default=False, required=False)
    parser.add_argument('-i', '--input', type=str,
                        default="tweeran.yaml", required=False)
    return parser.parse_args()


def extract(args: argparse.Namespace) -> tweeran.RedditExtractionResult:
    with open(args.input, "r") as f:
        config = yaml.safe_load(f)

    client = tweeran.RedditExtractionManager(
        config["reddit"]["subreddits"],
        config["wikidata_events"][0])

    result = client.run()

    # postprocess
    result.submissions["sentiment"] = result.submissions.apply(
        lambda x: tweeran.get_sentiment_from_text(x["title"]), axis=1)
    result.submissions["length"] = result.submissions.apply(
        lambda x: len(str(x["title"])) + len(str(x["selftext"])), axis=1)

    # extraction stores data locally by default
    result.comments.to_csv("data/reddit_comments.tsv", sep="\t")
    result.submissions.to_csv("data/reddit_submissions.tsv", sep="\t")
    result.users.to_csv("data/reddit_users.tsv", sep="\t")

    return result


def load_data() -> tweeran.RedditExtractionResult:
    return tweeran.RedditExtractionResult(
        submissions=pd.read_csv("data/reddit_submissions.tsv", sep="\t"),
        comments=pd.read_csv("data/reddit_comments.tsv", sep="\t"),
        users=pd.read_csv("data/reddit_users.tsv", sep="\t"))


def plot(data: tweeran.RedditExtractionResult):
    tweeran.viz.plot_reddit_data_over_time(
        data.submissions, "score", label="# of Ups/Downs")
    tweeran.viz.plot_reddit_data_over_time_subreddits(
        data.submissions, "num_comments", label="# of Comments")
    tweeran.viz.plot_reddit_data_over_time(
        data.submissions, "sentiment", label="Sentiment Score")
    tweeran.viz.plot_reddit_data_over_time_subreddits(
        data.submissions, "sentiment", label="Sentiment Score")
    tweeran.viz.plot_entities_frequencies(
        data.submissions, ["title", "selftext"])
    tweeran.viz.plot_subreddits_submissions(data)
    tweeran.viz.plot_submissions_length(data)
    tweeran.viz.plot_bigrams(data)
