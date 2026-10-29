"""Core analytics, run once by build.py and saved into SQLite for the dashboard.

1. Review scores: how negative each review's text sounds (out-of-fold, see below).
2. Aspect mentions: every sentence that mentions an aspect, with its negative score.
3. Similar pairs: near-identical reviews of the same product by different reviewer names.
"""
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import GroupKFold

from review_reality import sentiment
from review_reality.aspects import find_aspects, is_relevant, split_sentences

# A sentence counts as a complaint when the text model gives it at least this
# negative probability. Chosen after reading samples: at 0.5 too much praise
# was flagged; at 0.7 a hand check of 50 random sentences found 38 real complaints.
COMPLAINT_THRESHOLD = 0.7

SIMILARITY_THRESHOLD = 0.8  # cosine similarity of TF-IDF vectors, 1.0 = identical wording
MIN_SIMILAR_LENGTH = 60     # short texts like "Great product!" are naturally repeated


def out_of_fold_scores(reviews, folds=5):
    """Negative probability for every review, each scored by a model that never saw it.

    Reviews are split into 5 groups. For each group, a model is trained on the
    other 4 groups and scores this one. Identical texts stay in the same group.
    3-star reviews are never used for training but still get a score.
    """
    scores = pd.Series(np.nan, index=reviews.index)
    groups = reviews["text"].str.lower().str.strip()
    for train_idx, score_idx in GroupKFold(n_splits=folds).split(reviews, groups=groups):
        model = sentiment.train(reviews.iloc[train_idx])
        part = reviews.iloc[score_idx]
        scores.iloc[score_idx] = sentiment.negative_probability(model, part["text"])
    return pd.DataFrame({"review_id": reviews["review_id"], "text_neg_prob": scores.round(3)})


def aspect_mentions(reviews, model):
    """One row per (sentence, aspect) with the sentence's negative probability."""
    rows = [
        (review_id, number, sentence, aspect)
        for review_id, text, category in zip(reviews["review_id"], reviews["text"], reviews["category"])
        for number, sentence in enumerate(split_sentences(text))
        for aspect in find_aspects(sentence)
        if is_relevant(aspect, category)
    ]
    mentions = pd.DataFrame(rows, columns=["review_id", "sentence_no", "sentence", "aspect"])
    sentences = mentions[["review_id", "sentence_no", "sentence"]].drop_duplicates()
    sentences["neg_prob"] = sentiment.negative_probability(model, sentences["sentence"])
    return mentions.merge(sentences, on=["review_id", "sentence_no", "sentence"])


def similar_pairs(reviews):
    """Pairs of reviews of the same product family, by different reviewer names,
    whose wording is at least SIMILARITY_THRESHOLD similar."""
    pairs = []
    long_enough = reviews[reviews["text"].str.len() >= MIN_SIMILAR_LENGTH]
    for family, group in long_enough.groupby("family"):
        if len(group) < 2:
            continue
        vectors = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True).fit_transform(group["text"])
        ids = group["review_id"].to_numpy()
        users = group["reviewer_id"].to_numpy()
        for start in range(0, vectors.shape[0], 2000):  # in chunks to keep memory small
            similarity = (vectors[start:start + 2000] @ vectors.T).toarray()
            for i, j in zip(*np.nonzero(similarity >= SIMILARITY_THRESHOLD)):
                a = start + i
                if a < j and users[a] != users[j]:
                    pairs.append((int(ids[a]), int(ids[j]), round(float(similarity[i, j]), 3)))
    return pd.DataFrame(pairs, columns=["review_id_a", "review_id_b", "similarity"])


def run_all(clean):
    """Run every analysis. Returns a dict of DataFrames to save, plus model test scores."""
    metrics = sentiment.evaluate(clean)
    final_model = sentiment.train(clean)
    return {
        "review_scores": out_of_fold_scores(clean),
        "aspect_mentions": aspect_mentions(clean, final_model),
        "similar_pairs": similar_pairs(clean),
        "model_metrics": pd.DataFrame(sorted(metrics.items()), columns=["metric", "value"]),
    }
