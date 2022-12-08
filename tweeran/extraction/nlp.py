import spacy

spacy_nlp = spacy.load('en_core_web_sm', disable=["parser", "entity"])


def extract_tokens(text: str) -> list[str]:
    text = text.strip().replace("\n", " ").replace("\r", " ")
    text_features = spacy_nlp(text)
    return [tok.text for tok in text_features if not tok.is_stop]
