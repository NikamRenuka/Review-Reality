"""A small text model that estimates how negative a sentence or review sounds.

Why a model at all? Star ratings already tell us how happy a reviewer was
overall, but a 5-star review can still contain a complaint ("love it, but the
battery drains fast"). Stars cannot find that sentence; a text model can.

How it learns: we show it reviews with 1-2 stars (negative) and 4-5 stars
(positive); 3-star reviews are left out because they are mixed.
- TF-IDF turns text into numbers: each word or two-word phrase gets a weight
  that is high when it is frequent in this review but rare overall.
- Logistic regression learns which words push towards "negative".
- class_weight="balanced" stops it from ignoring the rare negative class
  (only about 4% of reviews are negative).

We test it on 20% of reviews that it never saw during training.
Copies of the same text are kept on the same side of the split, so the test is fair.
"""
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import make_pipeline

RANDOM_STATE = 42


def make_model():
    return make_pipeline(
        TfidfVectorizer(ngram_range=(1, 2), min_df=3, sublinear_tf=True),
        LogisticRegression(class_weight="balanced", max_iter=2000, random_state=RANDOM_STATE),
    )


def labelled(reviews):
    """Keep clearly negative (1-2 stars, label 1) and clearly positive (4-5 stars, label 0) reviews."""
    data = reviews[reviews["rating"] != 3]
    return data["text"], (data["rating"] <= 2).astype(int), data["text"].str.lower().str.strip()


def evaluate(reviews):
    """Train on 80% and test on the other 20%. Returns a dict of test scores."""
    texts, labels, groups = labelled(reviews)
    split = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=RANDOM_STATE)
    train_idx, test_idx = next(split.split(texts, labels, groups))
    model = make_model().fit(texts.iloc[train_idx], labels.iloc[train_idx])
    predicted = model.predict(texts.iloc[test_idx])
    actual = labels.iloc[test_idx]
    return {
        "test_reviews": int(len(test_idx)),
        "test_negative_reviews": int(actual.sum()),
        "balanced_accuracy": round(balanced_accuracy_score(actual, predicted), 3),
        "negative_precision": round(precision_score(actual, predicted), 3),
        "negative_recall": round(recall_score(actual, predicted), 3),
        "negative_f1": round(f1_score(actual, predicted), 3),
        # Baseline: always guess "positive" (the most common answer).
        "baseline_balanced_accuracy": 0.5,
        "baseline_negative_recall": 0.0,
    }


def train(reviews):
    """Train the final model on all labelled reviews."""
    texts, labels, _ = labelled(reviews)
    return make_model().fit(texts, labels)


def negative_probability(model, texts):
    """Probability (0 to 1) that each text sounds negative."""
    return np.round(model.predict_proba(list(texts))[:, 1], 3)
