"""Check every SQL file against answers worked out by hand on made-up test data."""
import pandas as pd
import pytest

from review_reality.db import query, write_database


def make_clean(rows):
    base = {
        "review_id": 0, "family": "Tablet A", "category": "Tablets", "listing_name": "Tablet A",
        "review_date": pd.Timestamp("2017-01-01"), "rating": 5, "title": "t", "text": "ok",
        "text_length": 2, "recommends": True, "helpful_votes": 0, "source_site": "Best Buy",
        "reviewer_id": "r1", "source_file": "2019_05",
    }
    df = pd.DataFrame([{**base, **row} for row in rows])
    df["review_id"] = range(1, len(df) + 1)
    return df


@pytest.fixture
def db(tmp_path):
    # Tablet A: ratings 5, 5, 4, 1  -> avg 3.75, 25% negative, 50% five-star
    # Battery B: ratings 5, 2       -> avg 3.5,  50% negative
    clean = make_clean([
        {"rating": 5, "review_date": pd.Timestamp("2017-01-01")},
        {"rating": 5, "review_date": pd.Timestamp("2017-01-01"), "recommends": None},
        {"rating": 4, "review_date": pd.Timestamp("2017-02-01"), "source_site": "Amazon"},
        {"rating": 1, "review_date": pd.Timestamp("2017-02-01"), "recommends": False},
        {"family": "Battery B", "category": "Batteries", "rating": 5},
        {"family": "Battery B", "category": "Batteries", "rating": 2},
    ])
    return write_database(clean, tmp_path / "test.db")


def test_product_summary(db):
    summary = query("product_summary", {"min_reviews": 1}, db_path=db).set_index("family")
    assert summary.loc["Tablet A", "reviews"] == 4
    assert summary.loc["Tablet A", "avg_rating"] == 3.75
    assert summary.loc["Tablet A", "pct_negative"] == 25.0
    assert summary.loc["Tablet A", "pct_five_star"] == 50.0
    # recommends: True, NULL, True, False -> 2 of 3 answers = 66.7% (NULL is ignored)
    assert summary.loc["Tablet A", "pct_recommend"] == 66.7
    assert summary.loc["Battery B", "pct_negative"] == 50.0


def test_product_summary_min_reviews_hides_small_products(db):
    summary = query("product_summary", {"min_reviews": 3}, db_path=db)
    assert summary["family"].tolist() == ["Tablet A"]


def test_rating_distribution_for_one_family_and_for_all(db):
    one = query("rating_distribution", {"family": "Tablet A"}, db_path=db)
    assert dict(zip(one["rating"], one["reviews"])) == {1: 1, 4: 1, 5: 2}
    assert one["pct"].sum() == 100.0
    everything = query("rating_distribution", {"family": None}, db_path=db)
    assert everything["reviews"].sum() == 6


def test_monthly_trend(db):
    trend = query("monthly_trend", {"family": "Tablet A"}, db_path=db)
    assert trend["month"].tolist() == ["2017-01", "2017-02"]
    assert trend["avg_rating"].tolist() == [5.0, 2.5]
    assert trend["pct_negative"].tolist() == [0.0, 50.0]


def test_review_bursts(db):
    # Battery B: 2 reviews on 2017-01-01 only -> typical 2/day, ratio 1.0
    # Tablet A: 2 reviews on each of two days  -> ratio 1.0
    assert query("review_bursts", {"family": None, "min_reviews": 2, "min_ratio": 1.5}, db_path=db).empty
    found = query("review_bursts", {"family": "Tablet A", "min_reviews": 2, "min_ratio": 1.0}, db_path=db)
    assert len(found) == 2


def test_source_comparison(db):
    result = query("source_comparison", {"family": "Tablet A", "min_reviews": 1}, db_path=db)
    assert dict(zip(result["source_site"], result["reviews"])) == {"Best Buy": 3, "Amazon": 1}


def test_database_rejects_invalid_rating(tmp_path):
    with pytest.raises(Exception):
        write_database(make_clean([{"rating": 7}]), tmp_path / "bad.db")
