"""Turn the raw review rows into one clean table.

Each function does one job, so it can be tested on its own.
`clean_reviews` runs them in order and records how many rows each step removed.
"""
import hashlib
import re

import pandas as pd

from review_reality.products import ASIN_NAMES, clean_listing_name, product_family

SITE_NAMES = {
    "bestbuy.com": "Best Buy",
    "amazon.com": "Amazon",
    "amazon.co.uk": "Amazon",
    "amazon.ca": "Amazon",
    "ebay.com": "eBay",
    "target.com": "Target",
    "newegg.com": "Newegg",
    "walmart.com": "Walmart",
}


def fill_listing_names(df):
    """Fill missing listing names: first from another row with the same ASIN, then from ASIN_NAMES."""
    df = df.copy()
    named = df.dropna(subset=["listing_name", "asins"])
    most_common_name = named.groupby("asins")["listing_name"].agg(lambda s: s.value_counts().index[0])
    first_asin = df["asins"].str.split(",").str[0]
    df["listing_name"] = (
        df["listing_name"]
        .fillna(df["asins"].map(most_common_name))
        .fillna(first_asin.map(ASIN_NAMES))
        .map(clean_listing_name)
    )
    return df


def add_product_family(df):
    """Add `family` and `category` columns from the listing name."""
    df = df.copy()
    pairs = df["listing_name"].map(product_family)
    df["family"] = pairs.str[0]
    df["category"] = pairs.str[1]
    return df


def parse_types(df):
    """Convert text columns into proper numbers, dates and true/false values.

    Values that cannot be converted become missing (NaN / NaT) instead of crashing.
    """
    df = df.copy()
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
    df.loc[~df["rating"].isin([1, 2, 3, 4, 5]), "rating"] = pd.NA
    df["helpful_votes"] = pd.to_numeric(df["helpful_votes"], errors="coerce")
    df.loc[df["helpful_votes"] < 0, "helpful_votes"] = pd.NA
    dates = pd.to_datetime(df["review_date"], errors="coerce", utc=True, format="ISO8601")
    df["review_date"] = dates.dt.tz_localize(None).dt.normalize()
    df["recommends"] = df["recommends"].str.strip().str.lower().map({"true": True, "false": False})
    return df


def source_site(url):
    """Return the shop name from the first URL in the field, e.g. 'Best Buy'."""
    if not isinstance(url, str):
        return "Unknown"
    match = re.search(r"https?://([^/,\s]+)", url)
    if not match:
        return "Unknown"
    host = match.group(1).lower()
    for domain, site in SITE_NAMES.items():
        if host == domain or host.endswith("." + domain):
            return site
    return "Other"


def normalise_text(text):
    """Lower-case and squeeze spaces, so tiny spacing differences do not hide a copy."""
    if not isinstance(text, str):
        return ""
    return re.sub(r"\s+", " ", text).strip().lower()


def reviewer_id(username):
    """Replace a username with a short anonymous code.

    The same username always gives the same code, so we can still count
    reviews per reviewer, but the name itself is not stored.
    """
    if not isinstance(username, str) or not username.strip():
        return None
    return hashlib.sha256(username.strip().lower().encode("utf-8")).hexdigest()[:12]


def drop_unusable(df):
    """Remove rows we cannot analyse: no rating, or no review text."""
    has_text = df["text"].fillna("").str.strip().str.len() > 0
    return df[df["rating"].notna() & has_text]


def drop_copies(df):
    """Keep one row per (product family, reviewer, review text).

    The same review is attached to several colour/size listings and appears in
    several snapshot files. We keep the copy from the newest file.
    """
    df = df.copy()
    df["_text_key"] = df["text"].map(normalise_text)
    df["_user_key"] = df["username"].fillna("").str.strip().str.lower()
    df = df.sort_values("source_file", ascending=False, kind="stable")
    df = df.drop_duplicates(subset=["family", "_user_key", "_text_key"], keep="first")
    return df.drop(columns=["_text_key", "_user_key"])


def clean_reviews(raw):
    """Run every cleaning step. Returns (clean table, list of (step, rows after step))."""
    steps = [("Raw rows (3 files stacked)", len(raw))]

    df = fill_listing_names(raw)
    df = add_product_family(df)
    df = parse_types(df)

    df = drop_unusable(df)
    steps.append(("After removing rows with no rating or no text", len(df)))

    df = drop_copies(df)
    steps.append(("After removing copied reviews", len(df)))

    df["source_site"] = df["source_url"].map(source_site)
    df["reviewer_id"] = df["username"].map(reviewer_id)
    df["text_length"] = df["text"].str.len()
    df["rating"] = df["rating"].astype(int)

    df = df.sort_values(["family", "review_date"], kind="stable").reset_index(drop=True)
    df.insert(0, "review_id", df.index + 1)

    columns = [
        "review_id", "family", "category", "listing_name", "review_date", "rating",
        "title", "text", "text_length", "recommends", "helpful_votes", "source_site",
        "reviewer_id", "source_file",
    ]
    return df[columns], steps
