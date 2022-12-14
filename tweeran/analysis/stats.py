
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from tweeran.nlp import spacy_nlp


def plot_entities_frequencies(data: pd.DataFrame, columns: list[str], exclude: str = "iran"):
    def extract_tokens(row) -> list[str]:
        tokens = []
        for c in columns:
            try:
                for ent in spacy_nlp(row[c]).ents:
                    if exclude in str(ent).lower():
                        continue
                    if ent.label_ in {'CARDINAL', 'ORDINAL', 'PERCENT', 'QUANTITY'}:
                        continue
                    tokens.append(ent.text)
            except ValueError:
                continue
        return tokens

    data["tokens"] = data.apply(extract_tokens, axis=1)  # type: ignore

    # groupby the values in the column, get the count and sort
    df_viz = data\
        .explode("tokens")\
        .groupby('tokens')["tokens"]\
        .count()\
        .reset_index(name='count')\
        .sort_values(['count'], ascending=False)\
        .head(10)\
        .reset_index(drop=True)

    sns.barplot(y=df_viz["tokens"], x=df_viz["count"])

    plt.ylabel("Entities")
    plt.xlabel("Frequencies")
    plt.savefig("reddit_frequencies.pdf", dpi=400, bbox_inches='tight')
    plt.close()
