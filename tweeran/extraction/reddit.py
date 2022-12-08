import io
import os

import praw

from tweeran.extraction.base import ExtractionManager
from tweeran.extraction.nlp import extract_tokens

MAX_NUMBER_SUBMISSIONS = 5000


class RedditExtractionManager(ExtractionManager):
    client: praw.Reddit
    output_path: os.PathLike | str
    subreddits: list[str]

    def __init__(
        self,
        client: praw.Reddit,
        output_path: os.PathLike | str,
        subreddits: list[str]
    ) -> None:
        super().__init__(output_path)
        self.client = client
        self.subreddits = subreddits
        self.buffer = open(
            output_path, mode="w+", buffering=io.DEFAULT_BUFFER_SIZE)

    def cleanup(self) -> None:
        self.buffer.close()

    def run(self) -> None:
        for subreddit_name in self.subreddits:
            subreddit = self.client.subreddit(subreddit_name)
            for p in subreddit.top(limit=MAX_NUMBER_SUBMISSIONS):
                self._write_post(p)

    def _write_post(self, p: praw.reddit.models.Submission):
        out = "\t".join(map(str, [
            p.id,
            p.created_utc,
            p.author,
            p.ups,
            p.downs,
            p.view_count,
            p.score,
            p.subreddit,
            p.num_comments,
            ",".join(extract_tokens(p.title)),
            ",".join(extract_tokens(p.selftext)),
        ]))
        self.buffer.write(f"{out}\n")
