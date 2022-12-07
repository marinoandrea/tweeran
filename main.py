import os

import dotenv
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


def main():
    dotenv.load_dotenv()

    client_stream = tweepy.StreamingClient(os.getenv("TWITTER_BEARER_TOKEN"))
    client_normal = tweepy.Client(os.getenv("TWITTER_BEARER_TOKEN"))

    tweeran.SearchExtractionManager(
        client_normal,
        "raw-data.tsv",
        RELEVANT_KEYWORDS,
        RELEVANT_HASHTAGS
    ).run()

    tweeran.StreamingExtractionManager(
        client_stream,
        "raw-data.tsv",
        RELEVANT_KEYWORDS,
        RELEVANT_HASHTAGS
    ).run()


if __name__ == '__main__':
    main()
