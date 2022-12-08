import os

import dotenv
import praw
import tweepy

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
    "iranpolitics"
]


def main():
    dotenv.load_dotenv()

    twitter_client_stream = tweepy.StreamingClient(
        os.getenv("TWITTER_BEARER_TOKEN"))
    twitter_client_normal = tweepy.Client(os.getenv("TWITTER_BEARER_TOKEN"))

    reddit_client = praw.Reddit(
        username=os.getenv("REDDIT_USERNAME"),
        password=os.getenv("REDDIT_PASSWORD"),
        client_id=os.getenv("REDDIT_CLIENTID"),
        client_secret=os.getenv("REDDIT_CLIENTSECRET"),
        user_agent="tweener"
    )

    tweeran.RedditExtractionManager(
        reddit_client,
        "raw-data_reddit.tsv",
        RELEVANT_SUBREDDITS
    ).run()

    tweeran.TwitterSearchExtractionManager(
        twitter_client_normal,
        "raw-data_twitter.tsv",
        RELEVANT_KEYWORDS,
        RELEVANT_HASHTAGS
    ).run()

    tweeran.TwitterStreamingExtractionManager(
        twitter_client_stream,
        "raw-data_twitter.tsv",
        RELEVANT_KEYWORDS,
        RELEVANT_HASHTAGS
    ).run()


if __name__ == '__main__':
    main()
