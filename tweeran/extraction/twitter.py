import io
import os
import time

import spacy
import tweepy

from tweeran.extraction.base import ExtractionManager
from tweeran.extraction.nlp import extract_tokens

spacy_nlp = spacy.load('en_core_web_sm', disable=["parser", "entity"])


class TwitterExtractionManager(ExtractionManager):
    keywords: list[str]
    hashtags: list[str]

    def __init__(
        self,
        output_path: os.PathLike | str,
        keywords: list[str],
        hashtags: list[str]
    ) -> None:
        super().__init__(output_path)
        self.keywords = keywords
        self.hashtags = hashtags


class TwitterStreamingExtractionManager(TwitterExtractionManager):
    client: tweepy.StreamingClient
    buffer: io.TextIOWrapper

    def __init__(
        self,
        client: tweepy.StreamingClient,
        output_path: os.PathLike | str,
        keywords: list[str],
        hashtags: list[str]
    ) -> None:
        super().__init__(output_path, keywords, hashtags)
        self.buffer = open(
            output_path, mode="w+", buffering=io.DEFAULT_BUFFER_SIZE)
        self.client = client
        self._initialize_client()

    def cleanup(self):
        self.buffer.close()

    def _initialize_client(self):
        rules = []
        terms = ' OR '.join(self.keywords)

        rules.append(tweepy.StreamRule(terms))
        for tag in self.hashtags:
            value = f"lang:en {tag}"
            rule = tweepy.StreamRule(value)
            rules.append(rule)

        # remove previous stream rules
        res = self.client.get_rules()
        if isinstance(res, tweepy.Response) and res.data:
            self.client.delete_rules(res.data)

        self.client.add_rules(add=rules)
        self.client.filter()

        self.client.on_tweet = self._on_tweet  # type: ignore

    def _on_tweet(self, t: tweepy.Tweet):
        out = "\t".join(map(str, [
            t.id,
            t.created_at,
            t.author_id,
            t.geo,
            t.context_annotations,
            t.public_metrics["retweet_count"],
            t.public_metrics["reply_count"],
            t.public_metrics["like_count"],
            t.public_metrics["quote_count"],
            ",".join(extract_tokens(t.text))
        ]))
        self.buffer.write(f"{out}\n")

    def run(self):
        while True:
            self.client.sample()
            time.sleep(1)


class TwitterSearchExtractionManager(TwitterExtractionManager):
    client: tweepy.Client

    def __init__(
        self,
        client: tweepy.Client,
        output_path: os.PathLike | str,
        keywords: list[str],
        hashtags: list[str]
    ) -> None:
        super().__init__(output_path, keywords, hashtags)
        self.client = client

    def cleanup(self) -> None:
        pass

    # TODO: implement run
