import io
import os
import time
from abc import ABC, abstractmethod

import spacy
import tweepy

spacy_nlp = spacy.load('en_core_web_sm', disable=["parser", "entity"])


class ExtractionManager(ABC):
    keywords: list[str]
    hashtags: list[str]
    output_path: os.PathLike | str

    def __init__(
        self,
        output_path: os.PathLike | str,
        keywords: list[str],
        hashtags: list[str]
    ) -> None:
        self.output_path = output_path
        self.keywords = keywords
        self.hashtags = hashtags

    def __del__(self):
        self.cleanup()

    @abstractmethod
    def cleanup(self) -> None:
        ...

    @abstractmethod
    def run(self) -> None:
        ...


class StreamingExtractionManager(ExtractionManager):
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
            value = f"lang:en {tag} OR ({terms})"
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
        text = t.text.strip().replace("\n", " ").replace("\r", " ")
        text_features = spacy_nlp(text)
        tokens = [tok.text for tok in text_features if not tok.is_stop]
        out = "\t".join(map(str, [
            t.id,
            t.created_at,
            t.author_id,
            t.geo,
            t.context_annotations,
            ",".join(tokens)
        ]))
        self.buffer.write(f"{out}\n")

    def run(self):
        while True:
            self.client.sample()
            time.sleep(1)


class SearchExtractionManager(ExtractionManager):
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
