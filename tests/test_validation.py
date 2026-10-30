"""Check the real database: SQL results must match an independent pandas calculation,
and the cleaned data must follow the rules we promised (no copies, no names, valid values).

Skipped when the database has not been built (python -m review_reality.build).
"""

import pandas as pd
import pytest

from review_reality.analytics import COMPLAINT_THRESHOLD
from review_reality.db import connect, query
from review_reality.paths import DB_PATH

pytestmark = pytest.mark.skipif(not DB_PATH.exists(), reason="database not built")


@pytest.fixture(scope="module")
def tables():
    with connect() as conn:
        reviews = pd.read_sql_query("SELECT * FROM reviews JOIN products USING (product_id)", conn)
        mentions = pd.read_sql_query("SELECT * FROM aspect_mentions", conn)
        steps = pd.read_sql_query("SELECT * FROM build_steps", conn)
    return reviews, mentions, steps


def test_row_count_matches_build_report(tables):
    reviews, _, steps = tables
    assert len(reviews) == steps["rows"].iloc[-1]


def test_product_summary_sql_matches_pandas(tables):
    reviews, _, _ = tables
    by_family = reviews.groupby("family")
    expected = pd.DataFrame({
        "reviews": by_family.size(),
        "avg_rating": by_family["rating"].mean().round(2),
        "pct_negative": (by_family["rating"].apply(lambda r: (r <= 2).mean()) * 100).round(1),
    })
    actual = query("product_summary", {"min_reviews": 1}).set_index("family")[["reviews", "avg_rating", "pct_negative"]]
    pd.testing.assert_frame_equal(actual.sort_index(), expected.sort_index(), check_dtype=False, check_names=False)


def test_aspect_summary_sql_matches_pandas(tables):
    reviews, mentions, _ = tables
    family = "AmazonBasics AAA Batteries"
    ids = set(reviews.loc[reviews["family"] == family, "review_id"])
    m = mentions[mentions["review_id"].isin(ids)]
    complaints = m[m["neg_prob"] >= COMPLAINT_THRESHOLD]
    expected = (complaints.groupby("aspect")["review_id"].nunique() / len(ids) * 100).round(2)
    actual = query("aspect_summary", {"family": family, "threshold": COMPLAINT_THRESHOLD}).set_index("aspect")
    for aspect, value in expected.items():
        assert actual.loc[aspect, "pct_reviews_complaining"] == pytest.approx(value, abs=0.01)


def test_no_copied_reviews_remain(tables):
    reviews, _, _ = tables
    key = reviews["text"].str.lower().str.split().str.join(" ")
    assert not pd.DataFrame({"f": reviews["family"], "u": reviews["reviewer_id"], "t": key}).duplicated().any()


def test_no_usernames_are_stored():
    with connect() as conn:
        columns = {row[1] for table in ("reviews", "products") for row in conn.execute(f"PRAGMA table_info({table})")}
    assert "username" not in columns
    assert "reviewer_id" in columns


def test_values_are_valid(tables):
    reviews, mentions, _ = tables
    assert reviews["rating"].between(1, 5).all()
    dates = pd.to_datetime(reviews["review_date"].dropna())
    assert dates.min() >= pd.Timestamp("2009-01-01") and dates.max() <= pd.Timestamp("2019-12-31")
    assert reviews["text"].str.strip().str.len().gt(0).all()
    assert mentions["neg_prob"].between(0, 1).all()
    assert mentions["review_id"].isin(reviews["review_id"]).all()  # every mention points to a real review
