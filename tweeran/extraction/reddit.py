from dataclasses import dataclass

import pandas as pd
import praw

from tweeran.nlp import clean, is_text_relevant

MAX_ENTRIES_DEFAULT = 10000

FEATURES_SUBMISSION = ["id", "created_utc", "author", "ups", "downs",
                       "view_count", "score", "subreddit", "num_comments",
                       "title", "selftext"]
FEATURES_COMMENT = ["id", "created_utc", "author", "body", "score"]


@dataclass
class RedditExtractionResult:
    submissions: pd.DataFrame
    comments: pd.DataFrame


class RedditExtractionManager:
    client: praw.Reddit
    subreddits: list[str]
    event_wikidata_id: str
    max_entries: int

    def __init__(
        self,
        client: praw.Reddit,
        subreddits: list[str],
        event_wikidata_id: str,
        max_entries: int = MAX_ENTRIES_DEFAULT
    ):
        self.client = client
        self.subreddits = subreddits
        self.event_wikidata_id = event_wikidata_id
        self.max_entries = max_entries

    def run(self) -> RedditExtractionResult:
        comments = []
        submissions = []
        submissions_ids = set()

        for subreddit_name in self.subreddits:
            subreddit = self.client.subreddit(subreddit_name)
            for s in subreddit.top(limit=self.max_entries):
                if (
                    not is_text_relevant(self.event_wikidata_id, s.title) and
                    not is_text_relevant(self.event_wikidata_id, s.selftext)
                ):
                    continue
                submissions.append({f: clean(getattr(s, f)) for f in FEATURES_SUBMISSION})
                submissions_ids.add(s.id)

            for c in subreddit.comments(limit=self.max_entries):
                if c.submission.id not in submissions_ids:
                    continue
                comments.append({f: clean(getattr(c, f)) for f in FEATURES_COMMENT})

        return RedditExtractionResult(
            submissions=pd.DataFrame(submissions, columns=FEATURES_SUBMISSION),
            comments=pd.DataFrame(comments, columns=FEATURES_COMMENT))
