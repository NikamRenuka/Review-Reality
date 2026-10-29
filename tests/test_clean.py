"""Tests for clean.py. The tiny tables here are made-up test data, not real reviews."""
import pandas as pd

from review_reality.clean import (
    clean_reviews,
    drop_copies,
    drop_unusable,
    normalise_text,
    parse_types,
    reviewer_id,
    source_site,
)


def raw_rows(rows):
    """Build a raw-shaped table (all text, like the CSV files) from a list of dicts."""
    base = {
        "listing_name": "Fire HD 8 Tablet, Black",
        "asins": "B000000001",
        "review_date": "2017-01-01T00:00:00.000Z",
        "rating": "5",
        "title": "t",
        "text": "Great tablet",
        "username": "alice",
        "recommends": "TRUE",
        "helpful_votes": "0",
        "source_url": "https://www.bestbuy.com/site/reviews/x",
        "source_file": "2019_05",
    }
    return pd.DataFrame([{**base, **row} for row in rows])


def test_parse_types_converts_and_rejects_bad_values():
    df = parse_types(raw_rows([
        {"rating": "4.0", "recommends": "False", "helpful_votes": "3"},
        {"rating": "6", "review_date": "not a date", "helpful_votes": "-1"},
        {"rating": "abc", "recommends": None},
    ]))
    assert df["rating"].tolist()[0] == 4
    assert df["rating"].isna().tolist()[1:] == [True, True]
    assert df["review_date"].iloc[0] == pd.Timestamp("2017-01-01")
    assert pd.isna(df["review_date"].iloc[1])
    assert df["recommends"].iloc[0] == False  # noqa: E712 (checking the value, not truthiness)
    assert pd.isna(df["recommends"].iloc[2])
    assert pd.isna(df["helpful_votes"].iloc[1])


def test_drop_unusable_removes_missing_rating_and_blank_text():
    df = parse_types(raw_rows([{"rating": "5"}, {"rating": None}, {"text": "   "}]))
    assert len(drop_unusable(df)) == 1


def test_drop_copies_keeps_one_copy_per_family_and_prefers_newest_file():
    df = raw_rows([
        {"source_file": "2018_04", "helpful_votes": "1"},
        {"source_file": "2019_05", "helpful_votes": "9", "text": "Great   TABLET "},  # same text, other spacing/case
        {"listing_name": "Echo (White)", "source_file": "2019_05"},  # same user+text, other family: keep
    ])
    df["family"] = ["Fire HD 8 Tablet", "Fire HD 8 Tablet", "Echo"]
    kept = drop_copies(df)
    assert len(kept) == 2
    assert kept.loc[kept["family"] == "Fire HD 8 Tablet", "helpful_votes"].item() == "9"


def test_drop_copies_keeps_different_reviewers():
    df = raw_rows([{"username": "alice"}, {"username": "bob"}])
    df["family"] = "Fire HD 8 Tablet"
    assert len(drop_copies(df)) == 2


def test_source_site():
    assert source_site("https://reviews.bestbuy.com/3545/x") == "Best Buy"
    assert source_site("https://www.amazon.com/dp/x,https://www.bestbuy.com/y") == "Amazon"
    assert source_site("https://redsky.target.com/x") == "Target"
    assert source_site("https://example.org/x") == "Other"
    assert source_site(None) == "Unknown"


def test_normalise_text():
    assert normalise_text("  Hello\n  WORLD ") == "hello world"


def test_reviewer_id_is_stable_and_hides_the_name():
    assert reviewer_id("Alice") == reviewer_id(" alice ")
    assert reviewer_id("alice") != reviewer_id("bob")
    assert "alice" not in reviewer_id("alice")
    assert reviewer_id(None) is None


def test_clean_reviews_end_to_end():
    raw = raw_rows([
        {"source_file": "2018_04"},
        {"source_file": "2019_05", "listing_name": "Fire HD 8 Tablet, Tangerine"},  # colour copy
        {"username": "bob", "rating": "1", "text": "Battery died", "listing_name": None},  # name filled by ASIN
        {"username": "carol", "rating": None},  # unusable
    ])
    clean, steps = clean_reviews(raw)
    assert [count for _, count in steps] == [4, 3, 2]
    assert clean["family"].tolist() == ["Fire HD 8 Tablet", "Fire HD 8 Tablet"]
    assert "username" not in clean.columns
    assert clean["review_id"].tolist() == [1, 2]
    assert clean["source_site"].unique().tolist() == ["Best Buy"]
