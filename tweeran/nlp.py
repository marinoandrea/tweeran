from functools import lru_cache
from typing import Any

import requests
import spacy
import vaderSentiment.vaderSentiment as vader

spacy_nlp = spacy.load('en_core_web_sm')


def extract_tokens(text: str) -> list[str]:
    text = text.strip().replace("\n", " ").replace("\r", " ")
    text_features = spacy_nlp(text)
    return [tok.text for tok in text_features if not tok.is_stop and not tok.is_punct]


def clean(value: Any) -> Any:
    if type(value) != str:
        return value
    return " ".join(str(value).strip().splitlines())


def get_sentiment_from_text(text: str) -> float:
    return vader\
        .SentimentIntensityAnalyzer()\
        .polarity_scores(text)["compound"]


@lru_cache
def get_wikidata_entity(wikidata_id: str) -> dict:
    api_endpoint = f"http://www.wikidata.org/entity/{wikidata_id}.json"
    res = requests.get(api_endpoint)
    return res.json()["entities"][wikidata_id]


@lru_cache
def get_wikipedia_article(title: str) -> str:
    api_endpoint = "https://en.wikipedia.org/w/api.php?" \
        + "action=query&format=json&" \
        + f"titles={title.replace(' ', '_')}&" \
        + "prop=extracts&exintro&explaintext"
    res = requests.get(api_endpoint)
    page = next(p for p in res.json()["query"]["pages"].values())
    return page["extract"]


@lru_cache
def get_related_entities(wikidata_ids: list[str]) -> set[str]:
    related_entities: set[str] = set()

    for wid in wikidata_ids:
        wikidata_entity = get_wikidata_entity(wid)

        label_features = spacy_nlp(wikidata_entity["labels"]["en"]["value"])
        desc_features = spacy_nlp(
            wikidata_entity["descriptions"]["en"]["value"])
        aliases_features = []
        for alias in wikidata_entity["aliases"].get("en", []):
            aliases_features.append(spacy_nlp(alias["value"]))

        ents = []
        for ent in label_features.ents:
            ents.append(ent)
        for ent in desc_features.ents:
            ents.append(ent)
        for alias_feat in aliases_features:
            for ent in alias_feat.ents:
                ents.append(ent)

        wikipedia_article = get_wikipedia_article(
            wikidata_entity["sitelinks"]["enwiki"]["title"])

        wikipedia_article_features = spacy_nlp(wikipedia_article)
        for ent in wikipedia_article_features.ents:
            ents.append(ent)

        # remove irrelevant entities
        final_ents = list(filter(
            lambda x: x.label_ not in {
                'CARDINAL', 'ORDINAL', 'PERCENT', 'QUANTITY'},
            ents))

        related_entities.update(
            set(map(lambda x: x.text.lower(), final_ents)))

    return related_entities


def is_text_relevant(event_wikidata_id: str, text: str) -> bool:
    related_entities = get_related_entities(event_wikidata_id)
    text_features = spacy_nlp(text)
    return any(e.text.lower() in related_entities for e in text_features.ents)


def get_bigrams(text: str):
    bigrams = []
    tokens = extract_tokens(text)
    for i in range(len(tokens) - 1):
        w1 = tokens[i].lower()
        w2 = tokens[i + 1].lower()
        if len(w1) < 2 or len(w2) < 2:
            continue
        vec = spacy_nlp(f"{w1} {w2}").vector
        bigrams.append((f"{w1}_{w2}", vec))
    return bigrams
