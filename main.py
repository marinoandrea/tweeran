import os

import dotenv
import pandas as pd
import praw

import tweeran

RELEVANT_HASHTAGS = [
    '#iran',
    '#iranprotests',
    '#mahsaamini',
    '#iranrevolution'
]

RELEVANT_KEYWORDS = [
    'Iran',
    'Iranian',
    'Mahsa',
    'Amini',
    'protests',
    'revolution',
]

RELEVANT_SUBREDDITS = [
    "iran",
    "iranian",
    "IranProtest2022",
    "iranprotests",
    "iranpolitics",
    "politics",
    "PoliticalDiscussion",
    "humanrights",
    "humanrightsdenied"
]

WIKIDATA_EVENT_ID = "Q114065797"  # Mahsa Amini protests


def main():
    dotenv.load_dotenv()

    reddit_client = praw.Reddit(
        username=os.getenv("REDDIT_USERNAME"),
        password=os.getenv("REDDIT_PASSWORD"),
        client_id=os.getenv("REDDIT_CLIENTID"),
        client_secret=os.getenv("REDDIT_CLIENTSECRET"),
        user_agent="tweener"
    )

    result = tweeran.RedditExtractionManager(
        client=reddit_client,
        subreddits=RELEVANT_SUBREDDITS,
        event_wikidata_id=WIKIDATA_EVENT_ID
    ).run()

    result.comments.to_csv("data/reddit_comments.tsv", sep="\t")
    result.submissions.to_csv("data/reddit_submissions.tsv", sep="\t")

    submissions = pd.read_csv("data/reddit_submissions.tsv", sep="\t")
    submissions["sentiment"] = submissions.apply(lambda x: tweeran.get_sentiment_from_text(x["title"]), axis=1)

    tweeran.plot_reddit_data_over_time(submissions, "num_comments", label="# of Comments")
    tweeran.plot_reddit_data_over_time_subreddits(submissions, "num_comments", label="# of Comments")

    tweeran.plot_reddit_data_over_time(submissions, "sentiment", label="Sentiment Score")
    tweeran.plot_reddit_data_over_time_subreddits(submissions, "sentiment", label="Sentiment Score")

    tweeran.plot_entities_frequencies(submissions, ["title", "selftext"])

    """
    TODO: relevant events for analysis
    [
        tweeran.TimelineEvent(date=date(2022, 9, 13), name="Arrest Mahsa Amini"),
        tweeran.TimelineEvent(date=date(2022, 9, 16), name="Death Mahsa Amini"),
        tweeran.TimelineEvent(date=date(2022, 9, 17), name="Funeral Protests"),
        tweeran.TimelineEvent(date=date(2022, 9, 22), name="National Protests"),
        tweeran.TimelineEvent(date=date(2022, 9, 30), name="Shootout Police Station"),
        tweeran.TimelineEvent(date=date(2022, 10, 3), name="Supreme Leader Talk"),
        tweeran.TimelineEvent(date=date(2022, 11, 21), name="Soccer Players Silent During Anthem"),
        tweeran.TimelineEvent(date=date(2022, 12, 4), name="Iran Abolishes Morality Police")
    ])
    """


if __name__ == '__main__':
    main()
