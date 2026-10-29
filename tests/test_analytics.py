"""Tests for aspects.py, sentiment.py and analytics.py. All texts here are made-up test data."""
import pandas as pd
import pytest

from review_reality import analytics, sentiment
from review_reality.aspects import find_aspects, is_relevant, split_sentences
from review_reality.db import query, write_analytics, write_database


def test_split_sentences():
    assert split_sentences("Great tablet! Battery dies fast.\nWould buy again") == [
        "Great tablet!", "Battery dies fast.", "Would buy again",
    ]
    assert split_sentences(None) == []


@pytest.mark.parametrize(
    "sentence, aspect",
    [
        ("The battery life is not too great.", "Battery life"),
        ("These batteries do not last as long as Duracell.", "Battery life"),
        ("Two of them leaked acid in my remote.", "Leaking"),
        ("It freezes a lot.", "Speed & performance"),
        ("Too many ads on the lock screen.", "Ads & special offers"),
        ("Alexa does not understand my questions.", "Voice assistant"),
        ("It keeps disconnecting from the wifi.", "Connectivity & setup"),
        ("Arrived dead out of the box.", "Defects & failures"),
    ],
)
def test_find_aspects(sentence, aspect):
    assert aspect in find_aspects(sentence)


def test_find_aspects_ignores_unrelated_sentence():
    assert find_aspects("I bought this for my husband.") == []


def test_question_box_is_not_a_voice_assistant_complaint():
    assert "Voice assistant" not in find_aspects("Some people asked a question in the question box.")


def test_remote_is_not_relevant_for_batteries():
    assert not is_relevant("Remote", "Batteries")
    assert is_relevant("Remote", "Streaming Media")


def toy_reviews(n_each=30):
    good = ["Love it, works great and the screen is beautiful.", "Excellent value, fast and easy to use."]
    bad = ["Terrible, it broke after a week and support was useless.", "Awful battery, dies fast, waste of money."]
    rows = []
    for i in range(n_each):
        rows.append({"rating": 5, "text": f"{good[i % 2]} Note {i}."})
        rows.append({"rating": 1, "text": f"{bad[i % 2]} Note {i}."})
    df = pd.DataFrame(rows)
    df["review_id"] = range(1, len(df) + 1)
    df["family"] = "Tablet A"
    df["category"] = "Tablets"
    df["reviewer_id"] = [f"r{i}" for i in range(len(df))]
    return df


def test_sentiment_model_separates_clear_cases():
    model = sentiment.train(toy_reviews())
    good, bad = sentiment.negative_probability(model, ["Love it, works great", "Terrible, broke, waste of money"])
    assert bad > 0.5 > good


def test_out_of_fold_scores_cover_every_review():
    reviews = toy_reviews()
    scores = analytics.out_of_fold_scores(reviews)
    assert len(scores) == len(reviews)
    assert scores["text_neg_prob"].between(0, 1).all()


def test_similar_pairs_finds_copies_by_different_names_only():
    text = "This tablet is just the right size for travel and the kids, with lots of great apps."
    reviews = pd.DataFrame({
        "review_id": [1, 2, 3, 4],
        "family": ["Tablet A"] * 4,
        "reviewer_id": ["a", "b", "a", "c"],
        "text": [text, text, text, "Completely different words about a speaker that sounds amazing in my kitchen."],
    })
    pairs = analytics.similar_pairs(reviews)
    # 1-2 and 2-3 are different names; 1-3 is the same name, so it is not reported.
    assert sorted(zip(pairs["review_id_a"], pairs["review_id_b"])) == [(1, 2), (2, 3)]


def test_aspect_summary_and_examples_sql(tmp_path):
    clean = pd.DataFrame({
        "review_id": [1, 2, 3, 4], "family": "Tablet A", "category": "Tablets", "listing_name": "Tablet A",
        "review_date": pd.to_datetime(["2017-01-05", "2017-02-05", "2017-04-05", "2017-04-06"]),
        "rating": [5, 1, 4, 5], "title": "t", "text": "x", "text_length": 1, "recommends": True,
        "helpful_votes": 0, "source_site": "Best Buy", "reviewer_id": ["a", "b", "c", "d"], "source_file": "2019_05",
    })
    db = write_database(clean, tmp_path / "t.db")
    mentions = pd.DataFrame({
        "review_id": [1, 2, 2, 3],
        "sentence_no": [0, 0, 1, 0],
        "sentence": ["Battery is fine.", "Battery died.", "Battery awful.", "Slow sometimes."],
        "aspect": ["Battery life", "Battery life", "Battery life", "Speed & performance"],
        "neg_prob": [0.1, 0.95, 0.9, 0.8],
    })
    write_analytics({"aspect_mentions": mentions, "review_scores": pd.DataFrame({"review_id": [1], "text_neg_prob": [0.1]})}, db)

    summary = query("aspect_summary", {"family": "Tablet A", "threshold": 0.7}, db_path=db).set_index("aspect")
    # Battery life: mentioned in reviews 1 and 2; complained about in review 2 only (2 sentences, 1 review).
    assert summary.loc["Battery life", "reviews_mentioning"] == 2
    assert summary.loc["Battery life", "reviews_complaining"] == 1
    assert summary.loc["Battery life", "pct_reviews_complaining"] == 25.0   # 1 of 4 reviews
    assert summary.loc["Battery life", "pct_mentions_negative"] == 66.7     # 2 of 3 sentences

    hidden = query("complaint_examples", {
        "family": "Tablet A", "aspect": "Speed & performance", "threshold": 0.7,
        "min_rating": 4, "max_rating": 5, "limit": 5}, db_path=db)
    assert hidden["sentence"].tolist() == ["Slow sometimes."]

    trend = query("aspect_trend", {"family": "Tablet A", "aspect": "Battery life", "threshold": 0.7, "min_reviews": 1}, db_path=db)
    assert dict(zip(trend["quarter"], trend["reviews_complaining"])) == {"2017-Q1": 1, "2017-Q2": 0}
