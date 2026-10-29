"""Save the clean reviews into SQLite and run the SQL files in sql/.

SQLite is a database that lives in a single file. It is built into Python,
so it costs nothing and needs no server.
"""
import sqlite3

import pandas as pd

from review_reality.paths import DB_PATH, SQL_DIR

SCHEMA = """
CREATE TABLE products (
    product_id   INTEGER PRIMARY KEY,
    family       TEXT NOT NULL UNIQUE,
    category     TEXT NOT NULL
);

CREATE TABLE reviews (
    review_id     INTEGER PRIMARY KEY,
    product_id    INTEGER NOT NULL REFERENCES products(product_id),
    listing_name  TEXT,
    review_date   TEXT,              -- 'YYYY-MM-DD'
    rating        INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
    title         TEXT,
    text          TEXT NOT NULL,
    text_length   INTEGER,
    recommends    INTEGER,           -- 1 = yes, 0 = no, NULL = not given
    helpful_votes INTEGER,
    source_site   TEXT,
    reviewer_id   TEXT,
    source_file   TEXT
);

CREATE INDEX idx_reviews_product ON reviews(product_id);
CREATE INDEX idx_reviews_date ON reviews(review_date);
"""


def write_database(clean, db_path=DB_PATH):
    """Create a fresh database file from the clean reviews table."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()  # always rebuild from the raw files, so results are reproducible

    products = (
        clean[["family", "category"]].drop_duplicates().sort_values("family").reset_index(drop=True)
    )
    products.insert(0, "product_id", products.index + 1)

    reviews = clean.merge(products[["product_id", "family"]], on="family").drop(columns=["family", "category"])
    reviews["review_date"] = reviews["review_date"].dt.strftime("%Y-%m-%d")
    reviews["recommends"] = reviews["recommends"].map({True: 1, False: 0})
    reviews["helpful_votes"] = reviews["helpful_votes"].astype("Int64")

    with sqlite3.connect(db_path) as conn:
        conn.executescript(SCHEMA)
        products.to_sql("products", conn, if_exists="append", index=False)
        reviews.to_sql("reviews", conn, if_exists="append", index=False)
    return db_path


ANALYTICS_INDEXES = """
CREATE INDEX IF NOT EXISTS idx_mentions_review ON aspect_mentions(review_id);
CREATE INDEX IF NOT EXISTS idx_mentions_aspect ON aspect_mentions(aspect);
CREATE INDEX IF NOT EXISTS idx_scores_review ON review_scores(review_id);
"""


def write_analytics(tables, db_path=DB_PATH):
    """Add the analytics tables (aspect_mentions, review_scores, ...) to the database."""
    with sqlite3.connect(db_path) as conn:
        for name, table in tables.items():
            table.to_sql(name, conn, if_exists="replace", index=False)
        conn.executescript(ANALYTICS_INDEXES)


def read_sql_file(name):
    return (SQL_DIR / f"{name}.sql").read_text(encoding="utf-8")


def query(name, params=None, db_path=DB_PATH):
    """Run sql/<name>.sql and return the result as a DataFrame.

    `params` fills the :placeholders in the SQL safely (never paste user input into SQL text).
    """
    with sqlite3.connect(db_path) as conn:
        return pd.read_sql_query(read_sql_file(name), conn, params=params or {})
