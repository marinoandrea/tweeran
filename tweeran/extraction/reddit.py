import os
from dataclasses import asdict, dataclass, field

import pandas as pd
import praw

from tweeran.nlp import clean, is_text_relevant

MAX_ENTRIES_DEFAULT = 10000

FEATURES_SUBMISSION = ["id", "created_utc", "author", "ups", "downs",
                       "view_count", "score", "subreddit", "num_comments",
                       "title", "selftext"]
FEATURES_COMMENT = ["id", "created_utc", "author", "body", "score"]
FEATURES_USER = ["id", "created_utc", "name", "comment_karma", "is_gold"]


@dataclass
class RedditExtractionResult:
    submissions: pd.DataFrame
    comments: pd.DataFrame
    users: pd.DataFrame


@dataclass
class RedditClientConfig:
    username: str | None = field(default=os.getenv("REDDIT_USERNAME"))
    password: str | None = field(default=os.getenv("REDDIT_PASSWORD"))
    client_id: str | None = field(default=os.getenv("REDDIT_CLIENTID"))
    client_secret: str | None = field(default=os.getenv("REDDIT_CLIENTSECRET"))


class RedditExtractionManager:
    client: praw.Reddit
    subreddits: list[str]
    event_wikidata_id: str
    max_entries: int

    def __init__(
        self,
        subreddits: list[str],
        event_wikidata_id: str,
        max_entries: int = MAX_ENTRIES_DEFAULT,
        client_config: RedditClientConfig = RedditClientConfig()
    ):
        self.subreddits = subreddits
        self.event_wikidata_id = event_wikidata_id
        self.max_entries = max_entries
        self.client = praw.Reddit(
            **asdict(client_config), user_agent="tweener")

    def run(self) -> RedditExtractionResult:
        comments = []
        submissions = []
        submissions_ids: set[str] = set()
        usernames: set[str] = set()

        for subreddit_name in self.subreddits:
            subreddit = self.client.subreddit(subreddit_name)
            for s in subreddit.top(limit=self.max_entries):
                if (
                    not is_text_relevant(self.event_wikidata_id, s.title) and
                    not is_text_relevant(self.event_wikidata_id, s.selftext)
                ):
                    continue
                submissions.append({f: clean(getattr(s, f))
                                   for f in FEATURES_SUBMISSION})
                submissions_ids.add(s.id)
                usernames.add(s.author)

            for c in subreddit.comments(limit=self.max_entries):
                if c.submission.id not in submissions_ids:
                    continue
                comments.append({f: clean(getattr(c, f))
                                for f in FEATURES_COMMENT})
                usernames.add(c.author)

        users = []
        for u in usernames:
            if u is None:
                continue
            result = self.client.redditor(u)
            if result is None:
                continue
            try:
                users.append({f: clean(getattr(result, f))
                             for f in FEATURES_USER})
            except Exception as e:
                print(result)
                raise e

        return RedditExtractionResult(
            submissions=pd.DataFrame(submissions, columns=FEATURES_SUBMISSION),
            comments=pd.DataFrame(comments, columns=FEATURES_COMMENT),
            users=pd.DataFrame(users, columns=FEATURES_USER))
