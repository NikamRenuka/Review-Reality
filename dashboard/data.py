"""Data access for the dashboard. Every function runs a SQL file from sql/ and caches the result,
so switching pages is instant and the numbers always come from the database."""
import sqlite3

import streamlit as st

from review_reality.analytics import COMPLAINT_THRESHOLD
from review_reality.db import query
from review_reality.paths import DB_PATH

MIN_PRODUCT_REVIEWS = 100   # products with fewer reviews are too small to describe fairly
REQUIRED_TABLES = {"products", "reviews", "aspect_mentions", "review_scores", "similar_pairs", "model_metrics", "build_steps"}


def database_ready():
    if not DB_PATH.exists():
        return False
    with sqlite3.connect(DB_PATH) as conn:
        tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
    return REQUIRED_TABLES <= tables


@st.cache_data(show_spinner="Loading…")
def run(name, **params):
    return query(name, params)


def products(min_reviews=MIN_PRODUCT_REVIEWS):
    return run("complaint_overview", threshold=COMPLAINT_THRESHOLD, min_reviews=min_reviews)


def product_names(min_reviews=MIN_PRODUCT_REVIEWS):
    return products(min_reviews)["family"].tolist()


def product_row(family):
    table = products(1)
    return table[table["family"] == family].iloc[0]


def summary(family):
    table = run("product_summary", min_reviews=1)
    return table[table["family"] == family].iloc[0]


def rating_distribution(family=None):
    return run("rating_distribution", family=family)


def aspects(family):
    return run("aspect_summary", family=family, threshold=COMPLAINT_THRESHOLD)


def aspect_trend(family, aspect, min_reviews=30):
    return run("aspect_trend", family=family, aspect=aspect, threshold=COMPLAINT_THRESHOLD, min_reviews=min_reviews)


def examples(family, aspect, min_rating=1, max_rating=5, limit=6):
    return run("complaint_examples", family=family, aspect=aspect, threshold=COMPLAINT_THRESHOLD,
               min_rating=min_rating, max_rating=max_rating, limit=limit)


def mismatches(family=None, high=0.9, low=0.1):
    return run("rating_text_mismatch", family=family, high=high, low=low)


def bursts(family=None, min_reviews=20, min_ratio=5):
    return run("review_bursts", family=family, min_reviews=min_reviews, min_ratio=min_ratio)


def daily(family):
    return run("daily_reviews", family=family)


def similar(family=None):
    """Reviews that belong to a near-identical pair (one row per review)."""
    return run("similar_reviews", family=family)


def similar_pairs():
    return table("similar_pairs")


def sources(family, min_reviews=20):
    return run("source_comparison", family=family, min_reviews=min_reviews)


@st.cache_data(show_spinner=False)
def table(name):
    """Read a small whole table (model_metrics, build_steps)."""
    import pandas as pd
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query(f"SELECT * FROM {name}", conn)  # name comes from our own code, never from users
